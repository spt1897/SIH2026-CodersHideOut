import os
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.warp import reproject, Resampling

def generate_ndvi_baseline(lulc_path, dem_path, output_path):
    """Memory-safe chunked generator for `ndvi_baseline.tif` matching the DEM grid."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    LULC_NDVI_MAP = {
        10: 0.75,  # Forest
        20: 0.45,  # Shrubland
        30: 0.50,  # Grassland
        40: 0.60,  # Cropland
        50: 0.05,  # Urban
        60: 0.00,  # Bare land
        70: 0.00,  # Snow/ice
        80: -0.20, # Water
        90: 0.55,  # Wetland
        95: 0.65,  # Mangroves
        100: 0.35  # Moss/lichen
    }

    print(f"Reading target raster profile from DEM: {dem_path}")
    with rasterio.open(dem_path) as dem_src:
        dem_profile = dem_src.profile.copy()
        dem_shape = (dem_src.height, dem_src.width)
        dem_transform = dem_src.transform
        dem_crs = dem_src.crs

    print(f"Deriving baseline values from LULC Mosaic (Memory-Safe Windowed Mode): {lulc_path}")
    
    # Update profile for output
    dem_profile.update({
        "dtype": "float32",
        "count": 1,
        "nodata": np.nan,
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256
    })

    with rasterio.open(lulc_path) as lulc_src:
        # If dimensions match, we process block-by-block; otherwise we use windowed reproject
        with rasterio.open(output_path, "w", **dem_profile) as dst:
            
            # Process in safe 2048x2048 pixel chunks to prevent RAM overflow
            block_size = 2048
            height, width = dem_shape
            
            for y in range(0, height, block_size):
                for x in range(0, width, block_size):
                    h = min(block_size, height - y)
                    w = min(block_size, width - x)
                    
                    window = Window(x, y, w, h)
                    window_transform = rasterio.windows.transform(window, dem_transform)
                    
                    # Create destination sub-array for this block
                    dest_block = np.full((h, w), np.nan, dtype=np.float32)
                    
                    # Reproject/read directly into window block safely
                    reproject(
                        source=rasterio.band(lulc_src, 1),
                        destination=dest_block,
                        src_transform=lulc_src.transform,
                        src_crs=lulc_src.crs,
                        dst_transform=window_transform,
                        dst_crs=dem_crs,
                        resampling=Resampling.nearest
                    )
                    
                    # Map LULC classes to NDVI baseline values vectorially per block
                    mapped_block = np.full((h, w), np.nan, dtype=np.float32)
                    for lulc_code, ndvi_val in LULC_NDVI_MAP.items():
                        mapped_block[dest_block == lulc_code] = ndvi_val
                        
                    # Fallback for unmapped valid classes
                    unmapped = (dest_block > 0) & np.isnan(mapped_block)
                    mapped_block[unmapped] = 0.30

                    # Write block to final output file
                    dst.write(mapped_block.astype(np.float32), 1, window=window)
                
                print(f"  Processed row chunk {y}/{height}...")

    print(f"\n[✓] Baseline NDVI derived successfully without RAM overflow!")
    print(f"Output saved to: {output_path}")

if __name__ == "__main__":
    lulc_mosaic_path = r"D:\File-Storage\static_features\landcover\processed\lulc_mosaic.tif"
    dem_reference_path = r"D:\File-Storage\static_features\dem\processed\dem_elevation.tif"
    output_ndvi_path = r"D:\File-Storage\static_features\landcover\processed\ndvi_baseline.tif"

    generate_ndvi_baseline(lulc_mosaic_path, dem_reference_path, output_ndvi_path)