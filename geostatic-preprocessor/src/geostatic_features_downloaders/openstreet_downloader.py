import os
import zipfile
import requests
from tqdm import tqdm

def download_ne_gis_datasets():
    # Base directory where all static features and vector data are stored
    output_dir = r"D:\File-Storage\static_features\openstreet-shapefile\data"
    os.makedirs(output_dir, exist_ok=True)

    # Downloads dictionary mapping target filename -> URL
    downloads = {
        # 1. Geofabrik OSM North-Eastern Zone Shapefiles (Roads, Buildings, Admin Areas, Landuse)
        "osm_north_east.zip": "https://download.geofabrik.de/asia/india/north-eastern-zone-latest-free.shp.zip",
        
        # 2. Raw OSM PBF File (Required to extract power, water, telecom, and oil/gas pipeline grids)
        "north-eastern-zone-latest.osm.pbf": "https://download.geofabrik.de/asia/india/north-eastern-zone-latest.osm.pbf",
        
        # 3. GEM Global Active Faults Database (Tectonic fault lines)
        "gem_active_faults.geojson": "https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults/master/geojson/gem_active_faults.geojson"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GIS Data Pipeline Ingestion"
    }

    print("========================================================")
    print("      Starting GIS Dataset Download Engine              ")
    print("========================================================\n")

    for filename, url in downloads.items():
        filepath = os.path.join(output_dir, filename)
        
        # Skip if file is already present
        if os.path.exists(filepath):
            print(f"[➜] Already exists: {filename}. Skipping download.")
        else:
            print(f"[+] Downloading {filename}...")
            try:
                response = requests.get(url, headers=headers, stream=True, timeout=60)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024 * 1024  # 1 MB chunk buffer

                with open(filepath, 'wb') as file, tqdm(
                    desc=filename,
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                    colour='green'
                ) as bar:
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            file.write(chunk)
                            bar.update(len(chunk))
                            
                print(f"[✓] Download complete: {filename}\n")
            except Exception as e:
                print(f"[✗] Failed to download {filename}: {e}\n")
                if os.path.exists(filepath):
                    os.remove(filepath)  # Remove incomplete corrupt downloads
                continue

        # Automatically extract .zip archives into the output directory
        if filename.endswith(".zip"):
            print(f"[-] Extracting shapefiles from {filename}...")
            try:
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                print(f"[✓] Extraction complete for {filename}\n")
            except Exception as e:
                print(f"[✗] Extraction failed for {filename}: {e}\n")

    print("========================================================")
    print("All datasets are ready in directory:")
    print(f"📁 '{output_dir}'")
    print("========================================================")

if __name__ == "__main__":
    download_ne_gis_datasets()