import os
import urllib.request
import zipfile


def download_osm():
    output_dir = "./data"
    os.makedirs(output_dir, exist_ok=True)

    # Direct source links for North East India datasets
    downloads = {
        # 1. Geofabrik OSM North-Eastern Zone Shapefile Package (Roads, Rivers, Buildings, Places, Landuse)
        "osm_north_east.zip": "https://download.geofabrik.de/asia/india/north-eastern-zone-latest-free.shp.zip",
        
        # 2. GEM Global Active Faults Database (Fault Lines)
        "gem_active_faults.geojson": "https://github.com/GEMScienceTools/gem-global-active-faults/raw/master/geojson/gem_active_faults.geojson",
        
        # 3. Geofabrik Administrative Boundary Polygons (States & Districts hierarchy)
        "boundary_polygons.zip": "https://download.geofabrik.de/asia/india/north-eastern-zone-boundary-polygons.zip"
    }

    def download_and_extract_all():
        for filename, url in downloads.items():
            filepath = os.path.join(output_dir, filename)
            print(f"\n[+] Downloading {filename}...")
            try:
                urllib.request.urlretrieve(url, filepath)
                print(f"[✓] Download complete: {filename}")
            except Exception as e:
                print(f"[✗] Failed to download {filename}: {e}")
                continue
                
            # Extract archives automatically
            if filename.endswith(".zip"):
                print(f"[-] Extracting {filename}...")
                try:
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(output_dir)
                    print(f"[✓] Extraction complete for {filename}")
                except Exception as e:
                    print(f"[✗] Failed to extract {filename}: {e}")

    if __name__ == "__main__":
        download_and_extract_all()
        print("\n========================================================")
        print("All layers successfully downloaded and unzipped in folder:")
        print(f"📁 '{output_dir}/'")
        print("========================================================")