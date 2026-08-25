import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

os.makedirs("./data", exist_ok=True)

# Exact ESA WorldCover 2021 v200 tile IDs covering Northeast India
tiles = [
    "N21E087", "N21E090", "N21E093", "N21E096",
    "N24E087", "N24E090", "N24E093", "N24E096",
    "N27E087", "N27E090", "N27E093", "N27E096"
]

base_url = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{}_Map.tif"

# Setup Session with Retry strategy & User-Agent header
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[500, 502, 503, 504],
    raise_on_status=False
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

for tile in tiles:
    url = base_url.format(tile)
    output_path = f"data/ESA_WorldCover_{tile}.tif"
    
    if os.path.exists(output_path):
        print(f"Skipping {tile}: Already exists.")
        continue
        
    print(f"Downloading WorldCover tile {tile}...")
    try:
        response = session.get(url, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                    if chunk:
                        f.write(chunk)
            print(f"[✓] Successfully saved: {output_path}")
        else:
            print(f"[!] Tile {tile} returned HTTP Status {response.status_code}")
    except Exception as e:
        print(f"[✗] Failed to download {tile}: {e}")