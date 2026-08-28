import math
import os
from typing import Dict, List, Tuple
import geopandas as gpd

from src.static_features_extractors.raster_file_config import VECTOR_PATHS


def get_vector_distances_batch(
    vector_key: str, coords: List[Tuple[float, float]], bbox: Tuple[float, float, float, float]
) -> Dict[Tuple[float, float], float]:
    """Crops a vector dataset to the specified bounding box (min_lat, min_lon, max_lat, max_lon)

    and computes the minimum distance in meters to nearest feature for all points.
    """
    results = {pt: 0.0 for pt in coords}
    path = VECTOR_PATHS.get(vector_key)

    if not path or not os.path.exists(path) or not coords:
        return results

    try:
        min_lat, min_lon, max_lat, max_lon = bbox
        
        # Read vector file filtered by bounding box (EPSG:4326)
        gdf = gpd.read_file(path, bbox=(min_lon, min_lat, max_lon, max_lat))
        if gdf.empty:
            return results

        # Project to planar CRS for accurate metric distance (EPSG:3857)
        gdf = gdf.to_crs(epsg=3857)

        # Convert coords into GeoDataFrame
        pts_gdf = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(
                [lon for lat, lon in coords], [lat for lat, lon in coords]
            ),
            crs="EPSG:4326",
        ).to_crs(epsg=3857)

        # Compute nearest spatial distances using R-Tree index
        for (lat, lon), pt_geom in zip(coords, pts_gdf.geometry):
            min_dist = gdf.distance(pt_geom).min()
            results[(lat, lon)] = float(min_dist)

    except Exception as e:
        print(f"Error calculating distances for {vector_key}: {e}")

    return results


def get_distance_to_fault_batch(
    coords: List[Tuple[float, float]], bbox: Tuple[float, float, float, float]
) -> Dict[Tuple[float, float], float]:
    return get_vector_distances_batch("faults", coords, bbox)


def get_distance_to_road_batch(
    coords: List[Tuple[float, float]], bbox: Tuple[float, float, float, float]
) -> Dict[Tuple[float, float], float]:
    return get_vector_distances_batch("roads", coords, bbox)


def get_distance_to_river_batch(
    coords: List[Tuple[float, float]], bbox: Tuple[float, float, float, float]
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
    bbox: Tuple[float, float, float, float],
    search_radius_m: float = 2000.0,
    is_length: bool = False,
) -> Dict[Tuple[float, float], float]:
    """Batch calculates building density or river drainage density within a search radius."""
    results = {pt: 0.0 for pt in coords}
    path = VECTOR_PATHS.get(vector_key)

    if not path or not os.path.exists(path) or not coords:
        return results

    try:
        min_lat, min_lon, max_lat, max_lon = bbox
        
        # Buffer bounding box to prevent clipping features near borders
        gdf = gpd.read_file(path, bbox=(min_lon - 0.05, min_lat - 0.05, max_lon + 0.05, max_lat + 0.05))
        if gdf.empty:
            return results

        gdf = gdf.to_crs(epsg=3857)
        area_km2 = math.pi * (search_radius_m / 1000.0) ** 2

        pts_gdf = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(
                [lon for lat, lon in coords], [lat for lat, lon in coords]
            ),
            crs="EPSG:4326",
        ).to_crs(epsg=3857)

        for (lat, lon), pt_geom in zip(coords, pts_gdf.geometry):
            buffer_zone = pt_geom.buffer(search_radius_m)
            clipped = gdf.clip(buffer_zone)

            if clipped.empty:
                results[(lat, lon)] = 0.0
            elif is_length:
                # Drainage density (km / km²)
                total_len_km = clipped.geometry.length.sum() / 1000.0
                results[(lat, lon)] = float(total_len_km / area_km2)
            else:
                # Building density (count / km²)
                results[(lat, lon)] = float(len(clipped) / area_km2)

    except Exception as e:
        print(f"Error computing density for {vector_key}: {e}")

    return results


def get_drainage_density_batch(
    coords: List[Tuple[float, float]], bbox: Tuple[float, float, float, float]
) -> Dict[Tuple[float, float], float]:
    return get_density_metrics_batch(
        "waterways", coords, bbox, is_length=True
    )


def get_building_density_batch(
    coords: List[Tuple[float, float]], bbox: Tuple[float, float, float, float]
) -> Dict[Tuple[float, float], float]:
    return get_density_metrics_batch(
        "buildings", coords, bbox, is_length=False
    )