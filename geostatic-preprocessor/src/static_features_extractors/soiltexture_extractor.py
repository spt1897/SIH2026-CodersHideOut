import os
from typing import Dict, List, Tuple
import numpy as np
import pyproj
import rasterio

from src.static_features_extractors.raster_file_config import SOIL_VRT_PATHS

# ISRIC SoilGrids native projection: Interrupted Goode Homolosine (IGH)
_IGH_PROJ = "+proj=igh +lat_0=0 +lon_0=0 +datum=WGS84 +units=m +no_defs"
_TRANSFORMER = pyproj.Transformer.from_crs(
    "EPSG:4326", _IGH_PROJ, always_xy=True
)


def get_soil_texture_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], Dict[str, int]]:
    """Batch extracts sand, silt, and clay soil percentages (0-100%) from local VRT files.

    Returns:
    - Dict mapping (lat, lon) -> {'soil_sand': int, 'soil_silt': int, 'soil_clay': int}
    """
    results = {
        pt: {"soil_sand": 0, "soil_silt": 0, "soil_clay": 0} for pt in coords
    }

    if not coords:
        return results

    # Pre-transform coordinates from WGS84 to SoilGrids native IGH projection
    igh_pts = [_TRANSFORMER.transform(lon, lat) for lat, lon in coords]

    for prop in ["sand", "silt", "clay"]:
        vrt_path = SOIL_VRT_PATHS.get(prop)
        if not vrt_path or not os.path.exists(vrt_path):
            continue

        try:
            with rasterio.open(vrt_path) as src:
                sampled = list(src.sample(igh_pts))
                for (lat, lon), val in zip(coords, sampled):
                    raw_val = val[0]
                    if (
                        raw_val is not None
                        and not np.isnan(raw_val)
                        and raw_val != src.nodata
                        and raw_val >= 0
                    ):
                        # Convert decig/kg to percentage integer (0-100)
                        pct = int(round(float(raw_val) / 10.0))
                        results[(lat, lon)][f"soil_{prop}"] = pct
        except Exception as e:
            print(f"Error sampling {prop} VRT: {e}")

    return results