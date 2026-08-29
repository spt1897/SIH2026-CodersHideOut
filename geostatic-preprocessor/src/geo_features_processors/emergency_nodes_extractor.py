import os
from typing import Dict, Tuple, Any, List
import h3
import shapely.geometry
import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from geopy.distance import geodesic

# Import your updated VECTOR_PATHS
from src.static_features_extractors.raster_file_config import VECTOR_PATHS

def extract_emergency_nodes(
    bbox: Tuple[float, float, float, float],
    h3_resolution: int,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Extracts top_k nearest emergency nodes for all H3 cells in a bounding box, 
    dynamically building the necessary spatial k-d trees internally.
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    bbox_tuple = (min_lon, min_lat, max_lon, max_lat) # GeoPandas format (xmin, ymin, xmax, ymax)
    
    # 1. Load and filter POI data for emergency trees
    category_filters = {
        "police": ["police", "police_station"],
        "fire": ["fire_station", "fire"],
        "hospital": ["hospital", "clinic", "health_post", "doctors"],
        "traffic_booth": ["traffic_signals", "checkpoint", "police_booth", "traffic_booth", "control_point"],
    }
    
    target_layers = ["pois", "pois_a", "traffic", "buildings"]
    combined_records = {cat: [] for cat in category_filters}

    for layer_name in target_layers:
        file_path = VECTOR_PATHS.get(layer_name)
        if not file_path or not os.path.exists(file_path):
            continue
            
        try:
            gdf = gpd.read_file(file_path, bbox=bbox_tuple)
            if gdf.empty:
                continue
            
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            elif gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            class_col = next((col for col in ["fclass", "type", "amenity", "building"] if col in gdf.columns), None)
            if not class_col:
                continue
                
            series_lower = gdf[class_col].astype(str).str.lower()
            for cat, terms in category_filters.items():
                matched_gdf = gdf[series_lower.isin(terms)].copy()
                if not matched_gdf.empty:
                    # Convert polygons to centroids for spatial trees
                    matched_gdf["geometry"] = matched_gdf["geometry"].apply(
                        lambda geom: geom.centroid if geom and geom.geom_type != "Point" else geom
                    )
                    matched_gdf = matched_gdf.dropna(subset=["geometry"])
                    combined_records[cat].append(matched_gdf)
        except Exception as e:
            print(f"[-] Error loading {layer_name}: {e}")

    # 2. Build KD-Trees
    emergency_trees = {}
    for cat_key, gdf_list in combined_records.items():
        if not gdf_list:
            emergency_trees[cat_key] = (None, gpd.GeoDataFrame(geometry=[], crs="EPSG:4326"))
            continue
            
        cat_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True), crs="EPSG:4326")
        pts, valid_indices = [], []
        for idx, row in cat_gdf.iterrows():
            geom = row.geometry
            if geom and not geom.is_empty:
                pts.append([geom.x, geom.y])
                valid_indices.append(idx)
                
        filtered_gdf = cat_gdf.loc[valid_indices].reset_index(drop=True)
        emergency_trees[cat_key] = (cKDTree(np.array(pts)), filtered_gdf) if pts else (None, gpd.GeoDataFrame(geometry=[], crs="EPSG:4326"))

    # 3. Generate H3 cells
    poly = h3.LatLngPoly([(min_lat, min_lon), (min_lat, max_lon), (max_lat, max_lon), (max_lat, min_lon), (min_lat, min_lon)])
    h3_cells = list(h3.polygon_to_cells(poly, res=h3_resolution))
    
    records = []

    # 4. Extract Nodes per H3 Cell
    for h3_index in h3_cells:
        lat, lon = h3.cell_to_latlng(h3_index)
        cell_point = (lat, lon)

        def query_nearest_category(cat_key: str):
            if cat_key not in emergency_trees or emergency_trees[cat_key][0] is None:
                return [], [], [], []
            tree, category_gdf = emergency_trees[cat_key]
            if category_gdf.empty:
                return [], [], [], []

            k_to_query = min(top_k, len(category_gdf))
            _, indices = tree.query([lon, lat], k=k_to_query)
            
            # Handle single vs multiple result indices from cKDTree
            if isinstance(indices, (int, np.integer)):
                indices = [indices]

            names, points, dists, contacts = [], [], [], []
            for idx in indices:
                row = category_gdf.iloc[idx]
                geom = row.geometry
                pt = geom if isinstance(geom, shapely.geometry.Point) else geom.centroid
                
                names.append(str(row.get('name', 'Unknown Facility')) if pd.notna(row.get('name')) else "Unknown Facility")
                points.append(f"SRID=4326;POINT({pt.x} {pt.y})")
                dists.append(round(geodesic(cell_point, (pt.y, pt.x)).km, 2))
                
                contact = "N/A"
                for col in ['phone', 'contact:phone', 'mobile']:
                    if col in row and pd.notna(row[col]):
                        contact = str(row[col])
                        break
                contacts.append(contact)
            return names, points, dists, contacts

        pn, pp, pd_dist, pc = query_nearest_category('police')
        fn, fp, fd_dist, fc = query_nearest_category('fire')
        hn, hp, hd_dist, hc = query_nearest_category('hospital')
        tn, tp, td_dist, tc = query_nearest_category('traffic_booth')

        records.append({
            "h3_index": h3_index,
            "police_names": pn, "police_points": pp, "police_distances_km": pd_dist, "police_contacts": pc,
            "fire_names": fn, "fire_points": fp, "fire_distances_km": fd_dist, "fire_contacts": fc,
            "hospital_names": hn, "hospital_points": hp, "hospital_distances_km": hd_dist, "hospital_contacts": hc,
            "traffic_booth_names": tn, "traffic_booth_points": tp, "traffic_booth_distances_km": td_dist, "traffic_booth_contacts": tc
        })

    # 5. Build asyncpg SQL Executemany Payload
    sql_tuples = [
        (
            r["h3_index"], r["police_names"], r["police_points"], r["police_distances_km"], r["police_contacts"],
            r["fire_names"], r["fire_points"], r["fire_distances_km"], r["fire_contacts"],
            r["hospital_names"], r["hospital_points"], r["hospital_distances_km"], r["hospital_contacts"],
            r["traffic_booth_names"], r["traffic_booth_points"], r["traffic_booth_distances_km"], r["traffic_booth_contacts"]
        ) for r in records
    ]

    sql_query = """
        INSERT INTO cell_emergency_nodes (
            h3_index, police_names, police_points, police_distances_km, police_contacts,
            fire_names, fire_points, fire_distances_km, fire_contacts,
            hospital_names, hospital_points, hospital_distances_km, hospital_contacts,
            traffic_booth_names, traffic_booth_points, traffic_booth_distances_km, traffic_booth_contacts
        ) VALUES (
            $1, $2, ARRAY(SELECT ST_GeomFromText(unnest($3::text[]), 4326)), $4, $5,
            $6, ARRAY(SELECT ST_GeomFromText(unnest($7::text[]), 4326)), $8, $9,
            $10, ARRAY(SELECT ST_GeomFromText(unnest($11::text[]), 4326)), $12, $13,
            $14, ARRAY(SELECT ST_GeomFromText(unnest($15::text[]), 4326)), $16, $17
        ) ON CONFLICT (h3_index) DO UPDATE SET
            police_names = EXCLUDED.police_names, police_points = EXCLUDED.police_points,
            police_distances_km = EXCLUDED.police_distances_km, police_contacts = EXCLUDED.police_contacts,
            fire_names = EXCLUDED.fire_names, fire_points = EXCLUDED.fire_points,
            fire_distances_km = EXCLUDED.fire_distances_km, fire_contacts = EXCLUDED.fire_contacts,
            hospital_names = EXCLUDED.hospital_names, hospital_points = EXCLUDED.hospital_points,
            hospital_distances_km = EXCLUDED.hospital_distances_km, hospital_contacts = EXCLUDED.hospital_contacts,
            traffic_booth_names = EXCLUDED.traffic_booth_names, traffic_booth_points = EXCLUDED.traffic_booth_points,
            traffic_booth_distances_km = EXCLUDED.traffic_booth_distances_km, traffic_booth_contacts = EXCLUDED.traffic_booth_contacts;
    """.strip()

    return {"records": records, "query": sql_query, "values": sql_tuples}