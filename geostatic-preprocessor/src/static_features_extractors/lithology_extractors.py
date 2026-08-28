import os
from typing import Dict, List, Tuple
import geopandas as gpd

from src.static_features_extractors.raster_file_config import GDB_PATH


def get_lithology_batch(
    coords: List[Tuple[float, float]], bbox: Tuple[float, float, float, float]
) -> Dict[Tuple[float, float], int]:
    """Intersects coordinate list with lithology GDB using a single spatial join query.

    Returns encoded integer (Defaults to 2).
    """
    results = {pt: 2 for pt in coords}

    if not os.path.exists(GDB_PATH) or not coords:
        return results

    try:
        min_lat, min_lon, max_lat, max_lon = bbox
        gdf = gpd.read_file(GDB_PATH, bbox=(min_lon, min_lat, max_lon, max_lat))
        if gdf.empty:
            return results

        pts_gdf = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(
                [lon for lat, lon in coords], [lat for lat, lon in coords]
            ),
            crs="EPSG:4326",
        ).to_crs(gdf.crs)

        # Execute single batch Spatial Join
        joined = gpd.sjoin(pts_gdf, gdf, how="left", predicate="within")

        col = (
            "lithology_encoded"
            if "lithology_encoded" in joined.columns
            else joined.columns[0]
        )

        for (lat, lon), litho_val in zip(coords, joined[col]):
            try:
                results[(lat, lon)] = 2 if int(litho_val) == 0 else int(litho_val)
            except Exception:
                results[(lat, lon)] = 2

    except Exception as e:
        print(f"Error processing lithology batch: {e}")

    return results