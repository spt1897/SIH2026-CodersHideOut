import os
import requests

def download_soil_type_texture():
    os.makedirs("./data", exist_ok=True)

    min_lon, min_lat, max_lon, max_lat = 89.0, 21.5, 97.5, 29.5

    # Updated ISRIC SoilGrids WCS 2.0.1 Endpoint for Soil Texture (USDA Class)
    isric_wcs_url = (
        "https://maps.isric.org/mapserv?map=/map/soilgrids.map&"
        "SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&"
        "COVERAGEID=clay_0-5cm_mean&"  # Or use soil texture / WRB coverage
        "FORMAT=image/tiff&"
        f"SUBSET=long({min_lon},{max_lon})&"
        f"SUBSET=lat({min_lat},{max_lat})"
    )

    # Alternative Direct High-Resolution Soil Texture Endpoint (WRB Class)
    wrb_url = (
        "https://maps.isric.org/mapserv?map=/map/wrb.map&"
        "SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&"
        "COVERAGEID=MostProbable&"
        "FORMAT=image/tiff&"
        f"SUBSET=long({min_lon},{max_lon})&"
        f"SUBSET=lat({min_lat},{max_lat})"
    )

    def download_soil_data(url, output_path):
        print(f"Downloading soil layer to {output_path}...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, stream=True, headers=headers, timeout=60)
        
        if response.status_code == 200 and not response.text.startswith("<HTML>"):
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            print(f"[✓] Saved successfully: {output_path}")
        else:
            print(f"[✗] Failed with status code {response.status_code}. Server returned non-image content.")

    download_soil_data(wrb_url, "data/ne_india_soil_type.tif")