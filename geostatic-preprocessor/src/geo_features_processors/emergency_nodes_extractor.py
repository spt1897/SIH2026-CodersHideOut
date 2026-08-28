from typing import Dict, List, Tuple
import h3
import shapely.geometry
import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from geopy.distance import geodesic

def extract_emergency_nodes(
    h3_index: str,
    emergency_trees: Dict[str, Tuple[cKDTree, gpd.GeoDataFrame]],
    top_k: int = 3
) -> Dict[str, any]:
    """Extracts top_k nearest emergency nodes for an H3 cell using k-d trees.
    Guarantees finding nearest nodes regardless of distance boundaries.

    Parameters:
    - h3_index: Target H3 cell ID string
    - emergency_trees: Pre-built k-d tree spatial lookup dictionary per category
    - top_k: Number of nearest facilities to record per category
    """
    # 1. Calculate cell centroid
    lat, lon = h3.cell_to_latlng(h3_index)
    cell_point = (lat, lon)

    # Helper function to query KD-Tree for top K nearest facilities
    def query_nearest_category(cat_key: str):
        if cat_key not in emergency_trees or emergency_trees[cat_key][0] is None:
            return [], [], [], []

        tree, category_gdf = emergency_trees[cat_key]
        if category_gdf.empty:
            return [], [], [], []

        # Query top-k nearest indices in 2D spatial coordinate space
        k_to_query = min(top_k, len(category_gdf))
        _, indices = tree.query([lon, lat], k=k_to_query)

        # Handle single vs multiple result indices
        if isinstance(indices, (int, np.integer)):
            indices = [indices]

        names, points, dists, contacts = [], [], [], []

        for idx in indices:
            row = category_gdf.iloc[idx]
            geom = row.geometry
            pt = geom if isinstance(geom, shapely.geometry.Point) else geom.centroid

            # Exact Geodesic distance calculation in kilometers
            dist_km = round(geodesic(cell_point, (pt.y, pt.x)).km, 2)

            # Facility Name
            name = str(row['name']) if 'name' in row and pd.notna(row['name']) else "Unknown Facility"
            
            # Contact Info
            contact = "N/A"
            for col in ['phone', 'contact:phone', 'mobile']:
                if col in row and pd.notna(row[col]):
                    contact = str(row[col])
                    break

            # WKT Point Geometry with SRID 4326 for PostGIS
            point_wkt = f"SRID=4326;POINT({pt.x} {pt.y})"

            names.append(name)
            points.append(point_wkt)
            dists.append(dist_km)
            contacts.append(contact)

        return names, points, dists, contacts

    # 2. Extract arrays per emergency category
    police_n, police_p, police_d, police_c = query_nearest_category('police')
    fire_n, fire_p, fire_d, fire_c = query_nearest_category('fire')
    hosp_n, hosp_p, hosp_d, hosp_c = query_nearest_category('hospital')
    traffic_n, traffic_p, traffic_d, traffic_c = query_nearest_category('traffic_booth')

    # 3. Return payload matching PostgreSQL Schema
    return {
        "h3_index": h3_index,
        "police_names": police_n,
        "police_points": police_p,
        "police_distances_km": police_d,
        "police_contacts": police_c,

        "fire_names": fire_n,
        "fire_points": fire_p,
        "fire_distances_km": fire_d,
        "fire_contacts": fire_c,

        "hospital_names": hosp_n,
        "hospital_points": hosp_p,
        "hospital_distances_km": hosp_d,
        "hospital_contacts": hosp_c,

        "traffic_booth_names": traffic_n,
        "traffic_booth_points": traffic_p,
        "traffic_booth_distances_km": traffic_d,
        "traffic_booth_contacts": traffic_c
    }