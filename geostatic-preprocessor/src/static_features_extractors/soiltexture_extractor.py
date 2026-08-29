import os
from typing import Dict, List, Tuple
import numpy as np
import pyproj
import rasterio

from src.static_features_extractors.raster_file_config import SOIL_VRT_PATHS

def get_soil_texture_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], Dict[str, float]]:
    """Batch extracts sand, silt, and clay soil values as float (percentage * 10).
    
    Value scale: 0.0 to 1000.0 (e.g., 425.0 = 42.5%).
    """
    results = {
        pt: {"soil_sand": 0.0, "soil_silt": 0.0, "soil_clay": 0.0} for pt in coords
    }

    if not coords:
        return results

    for prop in ["sand", "silt", "clay"]:
        target_path = SOIL_VRT_PATHS.get(prop)

        # Fallback to online streaming if local file doesn't exist
        if not target_path or not os.path.exists(target_path):
            target_path = SOIL_VRT_PATHS[prop]

        try:
            with rasterio.open(target_path) as src:
                # Dynamic CRS transform
                if src.crs and src.crs.to_string() != "EPSG:4326":
                    transformer = pyproj.Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
                    transformed_pts = [transformer.transform(lon, lat) for lat, lon in coords]
                else:
                    transformed_pts = [(lon, lat) for lat, lon in coords]

                sampled = list(src.sample(transformed_pts))

                for (lat, lon), val in zip(coords, sampled):
                    raw_val = val[0]
                    if (
                        raw_val is not None
                        and not np.isnan(raw_val)
                        and raw_val != src.nodata
                        and raw_val != -32768
                        and raw_val >= 0
                    ):
                        # Keep precise float value (percentage * 10)
                        results[(lat, lon)][f"soil_{prop}"] = float(raw_val)
                    else:
                        results[(lat, lon)][f"soil_{prop}"] = 0.0

        except Exception as e:
            print(f"Error sampling {prop}: {e}")

    return results