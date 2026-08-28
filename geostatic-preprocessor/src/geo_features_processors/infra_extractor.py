import os
import geopandas as gdp
from typing import List, Dict, Tuple, Any

from src.static_features_extractors.raster_file_config import VECTOR_PATHS

def fetch_infrastructure_by_bbox(bbox: Tuple[float, float, float, float]) -> Dict[str, List[Dict[str, Any]]]:
    """Queries all infrastructure layers from VECTOR_PATHS using a bounding box 
    and returns them structured to match the PostgreSQL schema completely.
    
    bbox format: (min_lat, min_lon, max_lat, max_lon)
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    bbox_tuple = (min_lon, min_lat, max_lon, max_lat) # GeoPandas format: (xmin, ymin, xmax, ymax)
    
    # Dictionary keys match your PostgreSQL table names
    tabular_data = {
        "roads": [],
        "railways": [],
        "rivers": [],
        "powerlines": [],
        "waterlines": [],
        "telecom": [],
        "oillines": []
    }

    for db_table, file_path in VECTOR_PATHS.items():
        if db_table not in tabular_data:
            continue
        if not os.path.exists(file_path):
            continue

        try:
            gdf = gdp.read_file(file_path, bbox=bbox_tuple)
            if gdf.empty:
                continue

            for idx, row in gdf.iterrows():
                geom_wkt = row.geometry.wkt if row.geometry else None
                if not geom_wkt:
                    continue

                if db_table == "roads":
                    row_data = {
                        "road_id": int(row.get("id", idx)),
                        "name": str(row.get("name")) if pd_notna(row.get("name")) else None,
                        "geom": geom_wkt
                    }
                elif db_table == "railways":
                    row_data = {
                        "railway_id": int(row.get("id", idx)),
                        "name": str(row.get("name")) if pd_notna(row.get("name")) else None,
                        "geom": geom_wkt
                    }
                elif db_table == "rivers":
                    row_data = {
                        "river_id": int(row.get("id", idx)),
                        "name": str(row.get("name")) if pd_notna(row.get("name")) else None,
                        "geom": geom_wkt
                    }
                elif db_table == "powerlines":
                    row_data = {
                        "powerline_id": int(row.get("id", idx)),
                        "name": str(row.get("name")) if pd_notna(row.get("name")) else None,
                        "geom": geom_wkt
                    }
                elif db_table == "waterlines":
                    row_data = {
                        "waterline_id": int(row.get("id", idx)),
                        "name": str(row.get("name")) if pd_notna(row.get("name")) else None,
                        "geom": geom_wkt
                    }
                elif db_table == "telecom":
                    row_data = {
                        "telecom_id": int(row.get("id", idx)),
                        "name": str(row.get("name")) if pd_notna(row.get("name")) else None,
                        "geom": geom_wkt
                    }
                elif db_table == "oillines":
                    row_data = {
                        "oilline_id": int(row.get("id", idx)),
                        "name": str(row.get("name")) if pd_notna(row.get("name")) else None,
                        "substance": str(row.get("substance")) if pd_notna(row.get("substance")) else "oil",
                        "geom": geom_wkt
                    }
                
                tabular_data[db_table].append(row_data)

        except Exception as e:
            print(f"[-] Error querying vector layer {db_table}: {e}")

    return tabular_data

def pd_notna(val):
    import pandas as pd
    return pd.notna(val)