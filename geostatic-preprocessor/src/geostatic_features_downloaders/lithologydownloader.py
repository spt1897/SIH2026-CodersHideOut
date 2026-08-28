import os
import requests
import zipfile


def download_extract_lithology():
    os.makedirs("data/zip", exist_ok=True)

    # Direct link to the Global Lithological Map Geodatabase archive
    glim_url = "https://www.dropbox.com/s/9vuowtebp9f1iud/LiMW_GIS%202015.gdb.zip?dl=1"
    zip_path = "zip/glim_gdb.zip"

    print("Downloading Global Lithological Map (GLiM) database (~100MB)...")
    response = requests.get(glim_url, stream=True)
    response.raise_for_status()

    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Extracting GLiM database...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("data/")

    print("Lithology dataset ready for GeoPandas spatial cropping!")