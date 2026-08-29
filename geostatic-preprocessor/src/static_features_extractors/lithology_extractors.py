import os
import json
import warnings
import pyogrio
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from typing import Dict, List, Tuple

# Bypasses pyogrio/GDAL polygon topology checks for massive multi-part geometries
os.environ["GDAL_ORGANIZATION_METHOD"] = "SKIP"
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pyogrio")

GDB_PATH = "D:/File-Storage/static_features/lithology/data/LiMW_GIS 2015.gdb"
MAPPING_JSON_PATH = "D:/File-Storage/static_features/master_lithology_mapping.json"


def get_lithology_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], int]:
    """
    Fast batch extraction of lithology encoded integers for a list of (lat, lon) coordinates.
    Directly returns a dictionary mapping (lat, lon) -> mapped_int.
    """
    # Initialize all points with 0 ('Unknown') matching .fillna(0) pipeline logic
    results: Dict[Tuple[float, float], int] = {pt: 0 for pt in coords}

    if not coords or not os.path.exists(GDB_PATH):
        if not os.path.exists(GDB_PATH):
            print(f"[-] GDB not found at: {GDB_PATH}")
        return results

    # 1. Load Master Mapping JSON
    master_map = {}
    if os.path.exists(MAPPING_JSON_PATH):
        try:
            with open(MAPPING_JSON_PATH, "r") as f:
                master_map = json.load(f)
        except Exception as e:
            print(f"[-] Error loading {MAPPING_JSON_PATH}: {e}")
            return results

    try:
        # 2. Build GeoDataFrame in EPSG:4326 (longitude, latitude)
        pts_gdf_4326 = gpd.GeoDataFrame(
            {"coord": coords},
            geometry=[Point(lon, lat) for lat, lon in coords],
            crs="EPSG:4326"
        )

        # 3. Read CRS info instantly without parsing heavy geometry
        info = pyogrio.read_info(GDB_PATH)
        gdb_crs = info["crs"]

        # 4. Reproject batch points to match GDB CRS
        pts_gdf = pts_gdf_4326.to_crs(gdb_crs)

        # Compute tight bounding box (plus 1000m padding) for instant spatial reading
        minx, miny, maxx, maxy = pts_gdf.total_bounds
        search_bbox = (minx - 1000, miny - 1000, maxx + 1000, maxy + 1000)

        # Read ONLY local polygons from disk covering the batch points
        gdf_subset = pyogrio.read_dataframe(GDB_PATH, bbox=search_bbox)

        if gdf_subset.empty:
            print("[-] No polygons found in GDB bounding box for this coordinate batch.")
            return results

        # Identify attribute column ('IDENTITY_' or 'lithology')
        col = 'lithology' if 'lithology' in gdf_subset.columns else gdf_subset.columns[0]

        # 5. Fast Spatial Join
        joined = gpd.sjoin(pts_gdf, gdf_subset[[col, 'geometry']], how="left", predicate="intersects")

        # 6. Extract raw string and lookup directly in master_map
        matched_count = 0
        for _, row in joined.iterrows():
            pt = row["coord"]

            # Skip if point was already successfully matched
            if results[pt] != 0:
                continue

            raw_val = row[col]
            if pd.notna(raw_val):
                raw_str = str(raw_val).strip()

                # Primary lookup: Raw value (e.g. 'IND201')
                # Fallback lookup: Prefixed value or Unknown
                encoded_val = master_map.get(
                    raw_str, 
                    master_map.get(f"1GEOSRF_{raw_str}", master_map.get("Unknown", 0))
                )

                if encoded_val != 0:
                    results[pt] = int(encoded_val)
                    matched_count += 1

        print(f"[✓] Lithology batch finished: {matched_count}/{len(coords)} points successfully encoded.")

    except Exception as e:
        print(f"[-] Lithology extraction error: {e}")

    return results

