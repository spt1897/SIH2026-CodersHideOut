import os
import glob
import zipfile
import numpy as np
import rasterio
from rasterio.merge import merge
import earthaccess


def download_extract_merge_dem():
    zip_dir = r"D:\File-Storage\static_features\dem\zip"
    unzip_dir = r"D:\File-Storage\static_features\dem\data"
    output_dir = r"D:\File-Storage\static_features\dem\processed"
    output_file = os.path.join(output_dir, "dem_elevation.tif")

    os.makedirs(zip_dir, exist_ok=True)
    os.makedirs(unzip_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------------------------------
    # 2. AUTHENTICATION & DOWNLOAD (NASA Earthdata)
    # -----------------------------------------------------------------------------
    auth = earthaccess.login(persist=True)

    # Bounding box for Northeast India
    ne_india_bbox = (89.0, 21.5, 97.5, 29.5)

    print("Searching for SRTM 30m DEM tiles...")
    results = earthaccess.search_data(
        short_name='SRTMGL1',
        bounding_box=ne_india_bbox
    )

    print(f"Found {len(results)} DEM tiles. Downloading...")
    earthaccess.download(results, zip_dir)
    print("[✓] DEM Download Complete!")



    print("Extracting DEM zip archives...")
    zip_files = glob.glob(os.path.join(zip_dir, "*.zip"))

    for zip_path in zip_files:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_dir)

    print(f"[✓] Extracted {len(zip_files)} archives to '{unzip_dir}'")


    print("\n=== Starting DEM Mosaicing ===")
    tile_paths = glob.glob(os.path.join(unzip_dir, "*.hgt")) + glob.glob(os.path.join(unzip_dir, "*.tif"))

    if not tile_paths:
        raise FileNotFoundError(f"No .hgt or .tif files found in '{unzip_dir}'")

    print(f"Mosaicing {len(tile_paths)} elevation tiles...")

    src_files = [rasterio.open(p) for p in tile_paths]

    try:
        # 1. Standard in-memory merge
        mosaic_array, out_trans = merge(src_files, method="first")
        
        # 2. Get nodata value (or default to SRTM void -32768)
        nodata_val = src_files[0].nodata if src_files[0].nodata is not None else -32768

        # 3. FIX: Cast array to float32 BEFORE replacing nodata with np.nan
        mosaic_array = mosaic_array.astype(np.float32)
        mosaic_array[mosaic_array == nodata_val] = np.nan

        # 4. Build output metadata with compression & block tiling
        out_meta = src_files[0].meta.copy()
        out_meta.update({
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
            "blockysize": 256
        })

       
        with rasterio.open(output_file, "w", **out_meta) as dst:
            dst.write(mosaic_array[0], 1)

        print(f"[✓] Continuous DEM Mosaic saved successfully to:\n    {output_file}")

    finally:
        for src in src_files:
            src.close()