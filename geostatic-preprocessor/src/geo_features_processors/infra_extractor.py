import os
import re
import geopandas as gpd
import pandas as pd
from typing import List, Dict, Tuple, Any
from src.static_features_extractors.raster_file_config import VECTOR_PATHS

def extract_osm_id(row: pd.Series, fallback_idx: int) -> int:
    """
    Extracts a clean integer OSM ID from various standard OSM attribute fields.
    Handles Geofabrik, OSMnx, Overpass, and QGIS vector shapefile formats.
    """
    # Candidate column names used across different OSM data sources
    candidate_keys = ["osm_id", "osmid", "@id", "id", "osm_way_id"]
    
    for key in candidate_keys:
        if key in row and pd.notna(row[key]):
            val = row[key]
            
            # If value is already an integer or float (e.g., 123456 or 123456.0)
            if isinstance(val, (int, float)):
                return int(val)
            
            # If value is a string (e.g., "way/123456", "123456", or "node/7890")
            if isinstance(val, str):
                digits = re.sub(r"\D", "", val)  # Extract only numeric digits
                if digits:
                    return int(digits)

    # Fallback if no valid OSM ID column or value exists
    return int(fallback_idx)


def fetch_infrastructure_by_bbox(
    bbox: Tuple[float, float, float, float],
    h3_resolution: int
) -> Dict[str, Any]:
    """Extracts infrastructure lines for a bounding box region and returns payload for native geom insertion."""
    
    min_lat, min_lon, max_lat, max_lon = bbox
    bbox_tuple = (min_lon, min_lat, max_lon, max_lat) 
    
    tabular_data = {t: [] for t in ["roads", "railways", "rivers", "powerlines", "waterlines", "telecom", "oillines"]}
    sql_payloads = {}

    for db_table, file_path in VECTOR_PATHS.items():
        if db_table not in tabular_data or not os.path.exists(file_path):
            continue
        try:
            gdf = gpd.read_file(file_path, bbox=bbox_tuple)
            if gdf.empty:
                continue

            for idx, row in gdf.iterrows():
                geom_wkt = row.geometry.wkt if row.geometry else None
                if not geom_wkt:
                    continue
                    
                # Robust extraction of actual OSM ID
                entity_id = extract_osm_id(row, idx)
                name = str(row.get("name")) if pd.notna(row.get("name")) else None

                if db_table == "roads":
                    tabular_data[db_table].append({"road_id": entity_id, "name": name, "geom": geom_wkt})
                elif db_table == "railways":
                    tabular_data[db_table].append({"railway_id": entity_id, "name": name, "geom": geom_wkt})
                elif db_table == "rivers":
                    tabular_data[db_table].append({"river_id": entity_id, "name": name, "geom": geom_wkt})
                elif db_table == "powerlines":
                    tabular_data[db_table].append({"powerline_id": entity_id, "name": name, "geom": geom_wkt})
                elif db_table == "waterlines":
                    tabular_data[db_table].append({"waterline_id": entity_id, "name": name, "geom": geom_wkt})
                elif db_table == "telecom":
                    tabular_data[db_table].append({"telecom_id": entity_id, "name": name, "geom": geom_wkt})
                elif db_table == "oillines":
                    substance = str(row.get("substance")) if pd.notna(row.get("substance")) else "oil"
                    tabular_data[db_table].append({"oilline_id": entity_id, "name": name, "substance": substance, "geom": geom_wkt})

        except Exception as e:
            print(f"[-] Error querying vector layer {db_table}: {e}")

    # Generate individual table bulk asyncpg queries
    for table_name, records in tabular_data.items():
        if not records:
            continue
        
        pk_col = f"{table_name[:-1]}_id" if table_name != "telecom" else "telecom_id"
        
        if table_name == "oillines":
            values = [(r[pk_col], r["name"], r["substance"], r["geom"]) for r in records]
            query = f"""
                INSERT INTO {table_name} ({pk_col}, name, substance, geom) 
                VALUES ($1, $2, $3, ST_GeomFromText($4, 4326)) 
                ON CONFLICT ({pk_col}) DO UPDATE SET name = EXCLUDED.name, substance = EXCLUDED.substance, geom = EXCLUDED.geom;
            """.strip()
        else:
            values = [(r[pk_col], r["name"], r["geom"]) for r in records]
            query = f"""
                INSERT INTO {table_name} ({pk_col}, name, geom) 
                VALUES ($1, $2, ST_GeomFromText($3, 4326)) 
                ON CONFLICT ({pk_col}) DO UPDATE SET name = EXCLUDED.name, geom = EXCLUDED.geom;
            """.strip()

        sql_payloads[table_name] = {"query": query, "values": values, "records": records}

    return sql_payloads