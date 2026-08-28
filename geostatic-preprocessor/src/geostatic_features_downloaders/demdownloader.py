import os
import glob
import zipfile
import numpy as np
import rasterio
from rasterio.merge import merge
import earthaccess
from scipy.ndimage import generic_filter


def compute_terrain_derivatives(dem_path, output_dir):
    """
    Computes Slope, Aspect, Curvature, TWI, SPI, and Roughness from the merged DEM
    and exports them as standalone GeoTIFF files.
    """
    print("\n=== Extracting DEM Derivatives ===")
    
    with rasterio.open(dem_path) as src:
        dem = src.read(1).astype(np.float32)
        transform = src.transform
        profile = src.profile.copy()

    # 1. Determine cell resolution in meters (approximate conversion if geographic CRS)
    res_x = abs(transform[0])
    res_y = abs(transform[4])
    if res_x < 0.01:  # CRS is in lat/lon degrees (~30m for SRTM)
        cell_size_x = res_x * 111320.0
        cell_size_y = res_y * 111320.0
    else:
        cell_size_x, cell_size_y = res_x, res_y

    # 2. Compute Gradients & Surface Derivatives
    dy, dx = np.gradient(dem, cell_size_y, cell_size_x)
    
    # Slope (degrees)
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)

    # Aspect (degrees clockwise from North)
    aspect_rad = np.arctan2(-dx, dy)
    aspect_deg = np.degrees(aspect_rad)
    aspect_deg = np.where(aspect_deg < 0, aspect_deg + 360, aspect_deg)

    # Curvature (Laplacian / 2nd Derivative)
    d2y, _ = np.gradient(dy, cell_size_y)
    _, d2x = np.gradient(dx, cell_size_x)
    curvature = -(d2x + d2y)

    # Roughness (Standard Deviation of elevation in 3x3 window)
    roughness = generic_filter(dem, np.nanstd, size=3)

    # Hydraulic Proxies (TWI & SPI)
    tan_slope = np.tan(slope_rad)
    tan_slope[tan_slope <= 0] = 0.001  # Prevent division by zero / negative logs

    # Specific Catchment Area proxy (cell resolution scaling)
    sca = ((cell_size_x + cell_size_y) / 2.0) * (1.0 + np.abs(dx) + np.abs(dy))
    
    twi = np.log(sca / tan_slope)
    spi = sca * tan_slope

    # Helper function to save derived layers
    def save_derivative(filename, data):
        file_path = os.path.join(output_dir, filename)
        profile.update(dtype=rasterio.float32, count=1, nodata=np.nan)
        with rasterio.open(file_path, "w", **profile) as dst:
            dst.write(data.astype(np.float32), 1)
        print(f"[✓] Saved: {filename}")

    # 3. Save all derived feature rasters
    derivatives = {
        "dem_slope.tiff": slope_deg,
        "dem_aspect.tiff": aspect_deg,
        "dem_curvature.tiff": curvature,
        "dem_twi.tiff": twi,
        "dem_spi.tiff": spi,
        "dem_roughness.tiff": roughness,
    }

    for name, data in derivatives.items():
        save_derivative(name, data)


def download_extract_merge_dem():
    zip_dir = r"D:\File-Storage\static_features\dem\zip"
    unzip_dir = r"D:\File-Storage\static_features\dem\data"
    output_dir = r"D:\File-Storage\static_features\dem\processed"
    output_file = os.path.join(output_dir, "dem_elevation.tif")

    os.makedirs(zip_dir, exist_ok=True)
    os.makedirs(unzip_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------------------------------
    # 1. AUTHENTICATION & DOWNLOAD (NASA Earthdata)
    # -----------------------------------------------------------------------------
    auth = earthaccess.login(persist=True)

    # Bounding box for Northeast India
    ne_india_bbox = (89.0, 21.5, 97.5, 29.5)

    print("Searching for SRTM 30m DEM tiles...")
    results = earthaccess.search_data(
        short_name="SRTMGL1", bounding_box=ne_india_bbox
    )

    print(f"Found {len(results)} DEM tiles. Downloading...")
    earthaccess.download(results, zip_dir)
    print("[✓] DEM Download Complete!")

    # -----------------------------------------------------------------------------
    # 2. EXTRACTION
    # -----------------------------------------------------------------------------
    print("Extracting DEM zip archives...")
    zip_files = glob.glob(os.path.join(zip_dir, "*.zip"))

    for zip_path in zip_files:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(unzip_dir)

    print(f"[✓] Extracted {len(zip_files)} archives to '{unzip_dir}'")

    # -----------------------------------------------------------------------------
    # 3. MOSAICING
    # -----------------------------------------------------------------------------
    print("\n=== Starting DEM Mosaicing ===")
    tile_paths = glob.glob(os.path.join(unzip_dir, "*.hgt")) + glob.glob(
        os.path.join(unzip_dir, "*.tif")
    )

    if not tile_paths:
        raise FileNotFoundError(
            f"No .hgt or .tif files found in '{unzip_dir}'"
        )

    print(f"Mosaicing {len(tile_paths)} elevation tiles...")
    src_files = [rasterio.open(p) for p in tile_paths]

    try:
        mosaic_array, out_trans = merge(src_files, method="first")

        nodata_val = (
            src_files[0].nodata
            if src_files[0].nodata is not None
            else -32768
        )
        mosaic_array = mosaic_array.astype(np.float32)
        mosaic_array[mosaic_array == nodata_val] = np.nan

        out_meta = src_files[0].meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": mosaic_array.shape[1],
                "width": mosaic_array.shape[2],
                "transform": out_trans,
                "count": 1,
                "dtype": "float32",
                "nodata": np.nan,
                "compress": "deflate",
                "tiled": True,
                "blockxsize": 256,
                "blockysize": 256,
            }
        )

        with rasterio.open(output_file, "w", **out_meta) as dst:
            dst.write(mosaic_array[0], 1)

        print(
            f"[✓] Continuous DEM Mosaic saved successfully to:\n    {output_file}"
        )

    finally:
        for src in src_files:
            src.close()

    # -----------------------------------------------------------------------------
    # 4. TERRAIN DERIVATIVE EXTRACTION
    # -----------------------------------------------------------------------------
    compute_terrain_derivatives(output_file, output_dir)


if __name__ == "__main__":
    download_extract_merge_dem()