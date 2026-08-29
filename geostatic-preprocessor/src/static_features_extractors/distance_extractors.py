import math
import os
from typing import Dict, List, Tuple
import geopandas as gpd
import pandas as pd

from src.static_features_extractors.raster_file_config import VECTOR_PATHS


def get_vector_distances_batch(
    vector_key: str, 
    coords: List[Tuple[float, float]], 
    bbox: Tuple[float, float, float, float] = None
) -> Dict[Tuple[float, float], float]:
    """Crops a vector dataset to the specified bounding box (min_lat, min_lon, max_lat, max_lon)
    and computes the minimum distance in meters to nearest feature for all points using R-Tree spatial indexes.
    """
    results = {pt: 0.0 for pt in coords}
    path = VECTOR_PATHS.get(vector_key)

    if not path or not os.path.exists(path) or not coords:
        return results

    # Compute bbox from coords if not passed
    if bbox is None:
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        bbox = (min(lats), min(lons), max(lats), max(lons))

    try:
        min_lat, min_lon, max_lat, max_lon = bbox
        
        # Buffer bbox slightly (0.05 deg ~ 5km) so nearby roads outside bbox aren't missed
        pad = 0.05
        gdf = gpd.read_file(
            path, 
            bbox=(min_lon - pad, min_lat - pad, max_lon + pad, max_lat + pad)
        )
        if gdf.empty:
            return results

        # Reproject both vector data and points to metric planar projection (EPSG:3857)
        gdf = gdf.to_crs(epsg=3857)

        pts_gdf = gpd.GeoDataFrame(
            {"coord": coords},
            geometry=gpd.points_from_xy(
                [lon for _, lon in coords], 
                [lat for lat, _ in coords]
            ),
            crs="EPSG:4326",
        ).to_crs(epsg=3857)

        # -------------------------------------------------------------
        # FAST: STRtree Vectorized Nearest Neighbor Search
        # -------------------------------------------------------------
        nearest = gpd.sjoin_nearest(
            pts_gdf, 
            gdf[['geometry']], 
            how="left", 
            distance_col="dist_m"
        )

        # Map computed distance back to coordinate dict
        for _, row in nearest.iterrows():
            pt = row["coord"]
            if pd.notna(row["dist_m"]):
                results[pt] = float(row["dist_m"])

    except Exception as e:
        print(f"Error calculating distances for {vector_key}: {e}")

    return results


def get_distance_to_fault_batch(
    coords: List[Tuple[float, float]], 
    bbox: Tuple[float, float, float, float] = None
) -> Dict[Tuple[float, float], float]:
    return get_vector_distances_batch("faults", coords, bbox)


def get_distance_to_road_batch(
    coords: List[Tuple[float, float]], 
    bbox: Tuple[float, float, float, float] = None
) -> Dict[Tuple[float, float], float]:
    return get_vector_distances_batch("roads", coords, bbox)


def get_distance_to_river_batch(
    coords: List[Tuple[float, float]], 
    bbox: Tuple[float, float, float, float] = None
) -> Dict[Tuple[float, float], float]:
    d1 = get_vector_distances_batch("waterways", coords, bbox)
    d2 = get_vector_distances_batch("water_bodies", coords, bbox)

    results = {}
    for pt in coords:
        results[pt] = float(min(d1.get(pt, 0.0), d2.get(pt, 0.0)))
    return results


def get_density_metrics_batch(
    vector_key: str,
    coords: List[Tuple[float, float]],
    bbox: Tuple[float, float, float, float] = None,
    search_radius_m: float = 2000.0,
    is_length: bool = False,
) -> Dict[Tuple[float, float], float]:
    """Batch calculates building density or river drainage density within a search radius."""
    results = {pt: 0.0 for pt in coords}
    path = VECTOR_PATHS.get(vector_key)

    if not path or not os.path.exists(path) or not coords:
        return results

    if bbox is None:
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        bbox = (min(lats), min(lons), max(lats), max(lons))

    try:
        min_lat, min_lon, max_lat, max_lon = bbox
        
        gdf = gpd.read_file(path, bbox=(min_lon - 0.05, min_lat - 0.05, max_lon + 0.05, max_lat + 0.05))
        if gdf.empty:
            return results

        gdf = gdf.to_crs(epsg=3857)
        area_km2 = math.pi * (search_radius_m / 1000.0) ** 2

        pts_gdf = gpd.GeoDataFrame(
            {"coord": coords},
            geometry=gpd.points_from_xy(
                [lon for _, lon in coords], 
                [lat for lat, _ in coords]
            ),
            crs="EPSG:4326",
        ).to_crs(epsg=3857)

        # Buffer points once in planar projection
        pts_gdf["buffer"] = pts_gdf.geometry.buffer(search_radius_m)
        buffers_gdf = pts_gdf.set_geometry("buffer")

        # Spatial Join Buffer with GDF features
        joined = gpd.sjoin(gdf, buffers_gdf, how="inner", predicate="intersects")

        if is_length:
            # Clip geometries for exact length inside buffer
            for pt, group in joined.groupby("coord"):
                pt_geom = pts_gdf.loc[pts_gdf["coord"] == pt, "geometry"].values[0]
                buf = pt_geom.buffer(search_radius_m)
                clipped = group.geometry.clip(buf)
                total_len_km = clipped.length.sum() / 1000.0
                results[pt] = float(total_len_km / area_km2)
        else:
            # Building count density
            counts = joined.groupby("coord").size()
            for pt, count in counts.items():
                results[pt] = float(count / area_km2)

    except Exception as e:
        print(f"Error computing density for {vector_key}: {e}")

    return results


def get_drainage_density_batch(
    coords: List[Tuple[float, float]], 
    bbox: Tuple[float, float, float, float] = None
) -> Dict[Tuple[float, float], float]:
    return get_density_metrics_batch("waterways", coords, bbox, is_length=True)


def get_building_density_batch(
    coords: List[Tuple[float, float]], 
    bbox: Tuple[float, float, float, float] = None
) -> Dict[Tuple[float, float], float]:
    return get_density_metrics_batch("buildings", coords, bbox, is_length=False)