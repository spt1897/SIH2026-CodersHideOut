import json
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from typing import Dict, Tuple

from src.static_features_extractors.raster_file_config import GDB_PATH

MAPPING_JSON_PATH = r"D:\File-Storage\static_features\openstreet-shapefile\data\lithology_mapping.json"

def get_bbox_lithology_grid(bbox: Tuple[float, float, float, float], resolution_deg: float = 0.01) -> Dict[Tuple[float, float], int]:
    """Generates a grid of lat/lon points within the given bounding box, 
    extracts lithology values from GDB_PATH, and maps them to integers via JSON.
    """
    results = {}
    min_lat, min_lon, max_lat, max_lon = bbox

    if not os.path.exists(GDB_PATH):
        print(f"[-] GDB path not found: {GDB_PATH}")
        return results

    # Load alphanumeric-to-integer mapping from JSON
    litho_mapping = {}
    if os.path.exists(MAPPING_JSON_PATH):
        try:
            with open(MAPPING_JSON_PATH, "r") as f:
                litho_mapping = json.load(f)
        except Exception:
            pass

    try:
        # 1. Read subset of GDB using bounding box
        gdf = gpd.read_file(GDB_PATH, bbox=(min_lon, min_lat, max_lon, max_lat))
        if gdf.empty:
            return results

        # 2. Generate point grid across bounding box
        lats = np.arange(min_lat, max_lat, resolution_deg)
        lons = np.arange(min_lon, max_lon, resolution_deg)
        
        coords = [(lat, lon) for lat in lats for lon in lons]
        if not coords:
            return results

        pts_gdf = gpd.GeoDataFrame(
            geometry=[Point(lon, lat) for lat, lon in coords],
            crs="EPSG:4326"
        ).to_crs(gdf.crs)

        # 3. Perform batch spatial join
        joined = gpd.sjoin(pts_gdf, gdf, how="left", predicate="within")

        # Automatically determine the correct lithology attribute column
        col = None
        for candidate in ["lithology", "LITHOLOGY", "lith_code", "CODE", "GRIDCODE", "lithology_encoded"]:
            if candidate in joined.columns:
                col = candidate
                break
        if not col:
            col = joined.columns[1] if len(joined.columns) > 1 else joined.columns[0]

        # 4. Map results to encoded numbers
        for idx, (_, row_data) in enumerate(joined.iterrows()):
            lat, lon = coords[idx]
            litho_val = row_data.get(col, 2)
            
            if pd_isna(litho_val):
                results[(lat, lon)] = 2
            else:
                code_str = str(litho_val).strip()
                results[(lat, lon)] = litho_mapping.get(code_str, 2)

    except Exception as e:
        print(f"Error processing bounding box lithology grid: {e}")

    return results

def pd_isna(val):
    import pandas as pd
    return pd.isna(val)