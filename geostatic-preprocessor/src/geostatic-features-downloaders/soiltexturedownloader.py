import os
import requests

# ==========================================================
# ISRIC SOILGRIDS DIRECT WEBDAV DOWNLOADER (Northeast India)
# ==========================================================

OUTPUT_DIR = r"D:\File-Storage\static_features\soiltype\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Direct file URLs from ISRIC's storage (using global VRT or clipped assets where applicable, 
# or direct COG links if available)
# Let's target the exact stable endpoints for the 0-5cm mean properties.
files_to_download = {
    "ne_india_sand.tif": "https://files.isric.org/soilgrids/latest/data/sand/sand_0-5cm_mean.vrt",
    "ne_india_silt.tif": "https://files.isric.org/soilgrids/latest/data/silt/silt_0-5cm_mean.vrt",
    "ne_india_clay.tif": "https://files.isric.org/soilgrids/latest/data/clay/clay_0-5cm_mean.vrt",
}

def download_file(filename, url):
    out_path = os.path.join(OUTPUT_DIR, filename)
    print(f"Downloading {filename} from WebDAV...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, stream=True, headers=headers, timeout=120)
        if response.status_code == 200:
            with open(out_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            print(f"[✓] Successfully downloaded: {out_path} (Size: {os.path.getsize(out_path)} bytes)")
        else:
            print(f"[✗] Failed {filename} with status code {response.status_code}")
    except Exception as e:
        print(f"[✗] Error downloading {filename}: {e}")

if __name__ == "__main__":
    for fname, f_url in files_to_download.items():
        download_file(fname, f_url)
    
    print("\nWebDAV download links processed!")