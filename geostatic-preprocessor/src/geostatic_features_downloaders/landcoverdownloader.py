import os
import glob
import rasterio
from rasterio.merge import merge
from rasterio.enums import Resampling
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def download_merge_landcover():
    download_dir = r"D:\File-Storage\static_features\landcover\data"
    output_dir = r"D:\File-Storage\static_features\landcover\processed"
    output_file = os.path.join(output_dir, "lulc_mosaic.tif")

    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------------------------------
    # 2. DOWNLOAD ESA WORLDCOVER TILES
    # -----------------------------------------------------------------------------
    tiles = [
        "N21E087", "N21E090", "N21E093", "N21E096",
        "N24E087", "N24E090", "N24E093", "N24E096",
        "N27E087", "N27E090", "N27E093", "N27E096"
    ]

    base_url = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{}_Map.tif"

    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    print("Downloading ESA WorldCover Tiles...")
    for tile in tiles:
        url = base_url.format(tile)
        dest_path = os.path.join(download_dir, f"ESA_WorldCover_{tile}.tif")
        
        if os.path.exists(dest_path):
            print(f"Skipping {tile}: Already exists.")
            continue
            
        print(f"Downloading WorldCover tile {tile}...")
        try:
            response = session.get(url, headers=headers, stream=True, timeout=30)
            if response.status_code == 200:
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                        if chunk:
                            f.write(chunk)
                print(f"[✓] Saved: {dest_path}")
            else:
                print(f"[!] Tile {tile} returned status {response.status_code}")
        except Exception as e:
            print(f"[✗] Failed to download {tile}: {e}")

    # -----------------------------------------------------------------------------
    # 3. DISK-STREAMING CATEGORICAL MOSAIC
    # -----------------------------------------------------------------------------
    print("\n=== Starting ESA WorldCover Mosaicing ===")
    tile_paths = glob.glob(os.path.join(download_dir, "*.tif"))

    if not tile_paths:
        raise FileNotFoundError(f"No .tif files found in '{download_dir}'")

    print(f"Mosaicing {len(tile_paths)} Landcover tiles using Nearest Neighbor...")

    src_files = [rasterio.open(p) for p in tile_paths]

    try:
        # Configure output creation options
        dst_kwds = {
            "compress": "lzw",
            "tiled": True,
            "blockxsize": 256,
            "blockysize": 256
        }

        # FIX: Use dst_path + mem_limit to stream chunks directly to disk instead of requesting 1.2+ GiB RAM
        merge(
            src_files,
            method="first",
            resampling=Resampling.nearest,  # Preserves integer class IDs
            dst_path=output_file,           # Directly writes output file
            mem_limit=512,                  # Limit memory window to 512 MB
            dst_kwds=dst_kwds
        )

        print(f"[✓] Categorical Landcover Mosaic saved successfully to:\n    {output_file}")

    finally:
        for src in src_files:
            src.close()