import os
import concurrent.futures
import requests


def download_soiltextures():
    SOIL_PROPERTIES = ["sand", "silt", "clay"]
    OUTPUT_DIR = r"D:\File-Storage\static_features\soiltype\data"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Directly stream the raw file via HTTP with a larger buffer chunk
    def download_file(prop):
        url = f"https://files.isric.org/soilgrids/latest/data/{prop}/{prop}_0-5cm_mean.vrt"
        out_path = os.path.join(OUTPUT_DIR, f"{prop}_0-5cm_mean.vrt")
        
        print(f"Starting parallel download: {prop}...")
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                    if chunk:
                        f.write(chunk)
        print(f"Finished downloading: {prop}")

    # Run downloads concurrently across threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(download_file, SOIL_PROPERTIES)