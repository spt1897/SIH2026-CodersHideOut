import os
import rasterio
from rasterio.warp import transform_bounds

# Define your target bounding box in WGS84 (min_lon, min_lat, max_lon, max_lat)
# Default set for Northeast India region
BBOX_WGS84 = (88.0, 21.5, 97.5, 29.5)

OUTPUT_DIR = r"D:\File-Storage\static_features\soiltype\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REMOTE_VRTS = {
    "sand": "https://files.isric.org/soilgrids/latest/data/sand/sand_0-5cm_mean.vrt",
    "silt": "https://files.isric.org/soilgrids/latest/data/silt/silt_0-5cm_mean.vrt",
    "clay": "https://files.isric.org/soilgrids/latest/data/clay/clay_0-5cm_mean.vrt",
}

for prop, url in REMOTE_VRTS.items():
    vsi_url = f"/vsicurl/{url}"
    output_tif = os.path.join(OUTPUT_DIR, f"{prop}_cropped.tif")
    
    print(f"Downloading clipped GeoTIFF for {prop}...")
    
    with rasterio.open(vsi_url) as src:
        # Reproject WGS84 bounding box to the raster's native IGH projection
        minx, miny, maxx, maxy = transform_bounds("EPSG:4326", src.crs, *BBOX_WGS84)
        
        # Calculate pixel window corresponding to bounding box
        window = src.window(minx, miny, maxx, maxy)
        
        # Read data within the window
        data = src.read(1, window=window)
        transform = src.window_transform(window)
        
        # Save cropped raster locally
        profile = src.profile.copy()
        profile.update({
            "height": data.shape[0],
            "width": data.shape[1],
            "transform": transform,
            "driver": "GTiff"
        })
        
        with rasterio.open(output_tif, "w", **profile) as dst:
            dst.write(data, 1)
            
    print(f"Saved: {output_tif}")