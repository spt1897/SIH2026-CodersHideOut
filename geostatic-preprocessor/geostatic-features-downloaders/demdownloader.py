import os
import earthaccess

# 1. Authenticate with your NASA EDL account
auth = earthaccess.login(persist=True)

# 2. Define Northeast India Bounding Box (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat)
ne_india_bbox = (89.0, 21.5, 97.5, 29.5)

# 3. Search for SRTM 30m DEM datasets overlapping the region
results = earthaccess.search_data(
    short_name='SRTMGL1',
    bounding_box=ne_india_bbox
)

print(f"Found {len(results)} DEM tiles. Downloading...")

# 4. Download files automatically to your 'data' folder
os.makedirs("./data", exist_ok=True)
files = earthaccess.download(results, './data')
print("DEM Download Complete!")