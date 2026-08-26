import io
import os
import time
import zlib
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import rasterio
from rasterio.windows import Window
from scipy.ndimage import uniform_filter


def process_tile_in_memory(args):
    """Processes a single tile purely in memory.

    Compresses tile buffers before returning over IPC to maintain minimal memory
    overhead and eliminate disk I/O bottlenecks.
    """
    (
        dem_path,
        x,
        y,
        tile_size,
        halo,
        height,
        width,
        cell_size_x,
        cell_size_y,
        tile_idx,
    ) = args

    # Account for halo padding at boundaries
    y_start = max(0, y - halo)
    y_end = min(height, y + tile_size + halo)
    x_start = max(0, x - halo)
    x_end = min(width, x + tile_size + halo)

    with rasterio.open(dem_path) as src:
        read_window = Window(x_start, y_start, x_end - x_start, y_end - y_start)
        dem_chunk = src.read(1, window=read_window).astype(np.float32)

    # 1. Slope, Aspect, & Curvature Gradients
    dy, dx = np.gradient(dem_chunk, cell_size_y, cell_size_x)

    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)

    aspect_rad = np.arctan2(-dx, dy)
    aspect_deg = np.degrees(aspect_rad)
    aspect_deg = np.where(aspect_deg < 0, aspect_deg + 360.0, aspect_deg)

    d2y, _ = np.gradient(dy, cell_size_y)
    _, d2x = np.gradient(dx, cell_size_x)
    curvature = -(d2x + d2y)

    # 2. Surface Roughness
    mean = uniform_filter(dem_chunk, size=3)
    mean_sq = uniform_filter(dem_chunk**2, size=3)
    var = mean_sq - mean**2
    var[var < 0] = 0.0
    roughness = np.sqrt(var)

    # 3. Hydrological Indices (TWI & SPI)
    tan_slope = np.tan(slope_rad)
    tan_slope[tan_slope <= 0] = 0.001
    sca = ((cell_size_x + cell_size_y) / 2.0) * (1.0 + np.abs(dx) + np.abs(dy))
    twi = np.log(sca / tan_slope)
    spi = sca * tan_slope

    # Trim halo padding back to target window dimensions
    slice_y_start = y - y_start
    slice_y_end = slice_y_start + min(tile_size, height - y)
    slice_x_start = x - x_start
    slice_x_end = slice_x_start + min(tile_size, width - x)

    write_h = slice_y_end - slice_y_start
    write_w = slice_x_end - slice_x_start

    tile_data = {
        "dem_slope.tiff": slope_deg[
            slice_y_start:slice_y_end, slice_x_start:slice_x_end
        ],
        "dem_aspect.tiff": aspect_deg[
            slice_y_start:slice_y_end, slice_x_start:slice_x_end
        ],
        "dem_curvature.tiff": curvature[
            slice_y_start:slice_y_end, slice_x_start:slice_x_end
        ],
        "dem_twi.tiff": twi[
            slice_y_start:slice_y_end, slice_x_start:slice_x_end
        ],
        "dem_spi.tiff": spi[
            slice_y_start:slice_y_end, slice_x_start:slice_x_end
        ],
        "dem_roughness.tiff": roughness[
            slice_y_start:slice_y_end, slice_x_start:slice_x_end
        ],
    }

    # Compress numpy buffers in RAM (Zero Disk Writes)
    compressed_buffers = {}
    for name, arr in tile_data.items():
        mem_file = io.BytesIO()
        np.save(mem_file, arr.astype(np.float32))
        raw_bytes = mem_file.getvalue()
        compressed_buffers[name] = zlib.compress(raw_bytes, level=1)

    return x, y, write_w, write_h, compressed_buffers


def extract_dem_derivatives_robust(
    dem_path, output_dir, tile_size=2048, max_workers=4
):
    """Executes chunked extraction using compressed in-memory IPC streams."""
    start_time = time.time()
    os.makedirs(output_dir, exist_ok=True)

    with rasterio.open(dem_path) as src:
        height, width = src.height, src.width
        transform = src.transform
        profile = src.profile.copy()

    # Spatial resolution scaling for physical parameters
    res_x = abs(transform[0])
    res_y = abs(transform[4])
    cell_size_x = res_x * 111320.0 if res_x < 0.01 else res_x
    cell_size_y = res_y * 111320.0 if res_y < 0.01 else res_y

    derivative_names = [
        "dem_slope.tiff",
        "dem_aspect.tiff",
        "dem_curvature.tiff",
        "dem_twi.tiff",
        "dem_spi.tiff",
        "dem_roughness.tiff",
    ]

    out_meta = profile.copy()
    out_meta.update(
        {
            "dtype": "float32",
            "count": 1,
            "nodata": np.nan,
            "compress": "deflate",
            "tiled": True,
            "blockxsize": 256,
            "blockysize": 256,
        }
    )

    writers = {
        name: rasterio.open(os.path.join(output_dir, name), "w", **out_meta)
        for name in derivative_names
    }

    try:
        tasks = []
        tile_idx = 0
        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):
                tasks.append(
                    (
                        dem_path,
                        x,
                        y,
                        tile_size,
                        2,
                        height,
                        width,
                        cell_size_x,
                        cell_size_y,
                        tile_idx,
                    )
                )
                tile_idx += 1

        total_tiles = len(tasks)
        print(
            f"Processing {total_tiles} tiles using Memory-Compressed IPC (Workers: {max_workers})..."
        )

        completed = 0
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_tile_in_memory, task) for task in tasks
            ]

            for future in as_completed(futures):
                x, y, write_w, write_h, compressed_buffers = future.result()
                write_window = Window(x, y, write_w, write_h)

                # Decompress in main process RAM and write directly to GeoTIFF rasters
                for name, compressed_bytes in compressed_buffers.items():
                    decompressed_bytes = zlib.decompress(compressed_bytes)
                    mem_file = io.BytesIO(decompressed_bytes)
                    arr = np.load(mem_file)
                    writers[name].write(arr, 1, window=write_window)

                completed += 1
                elapsed = time.time() - start_time
                print(
                    f"[✓] Completed {completed}/{total_tiles} tiles ({completed / total_tiles * 100:.1f}%) | Elapsed: {elapsed / 60:.2f} m"
                )

    finally:
        for w in writers.values():
            w.close()

    print(
        f"\n[✓] Successfully processed all {total_tiles} tiles across 6 rasters in {(time.time() - start_time) / 60:.2f} minutes!"
    )


if __name__ == "__main__":
    input_dem = (
        r"D:\File-Storage\static_features\dem\processed\dem_elevation.tif"
    )
    output_directory = r"D:\File-Storage\static_features\dem\processed"

    # Set max_workers to 4 to balance processing speed and system stability
    extract_dem_derivatives_robust(
        input_dem, output_directory, tile_size=2048, max_workers=4
    )