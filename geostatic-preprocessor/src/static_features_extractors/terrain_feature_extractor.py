import os
from typing import Dict, List, Tuple
import numpy as np
import rasterio

from src.static_features_extractors.raster_file_config import RASTER_PATHS


def sample_raster_batch(
    raster_path: str, coords: List[Tuple[float, float]], is_integer: bool = False
) -> Dict[Tuple[float, float], float]:
    """Helper to sample coordinates in batch from a single raster file.

    Parameters:
    - raster_path: Path to the GeoTIFF
    - coords: List of (lat, lon) tuples
    - is_integer: If True, casts output values to int (e.g. LULC / Soil Type)

    Returns:
    - Dict mapping (lat, lon) -> pixel_value
    """
    results = {pt: (0 if is_integer else 0.0) for pt in coords}

    if not os.path.exists(raster_path) or not coords:
        return results

    try:
        with rasterio.open(raster_path) as src:
            # Note: rasterio sample expects (x, y) = (lon, lat)
            pts_lon_lat = [(lon, lat) for lat, lon in coords]
            sampled_values = list(src.sample(pts_lon_lat))

            for (lat, lon), val in zip(coords, sampled_values):
                raw_val = val[0]
                if (
                    raw_val is None
                    or raw_val == src.nodata
                    or np.isnan(raw_val)
                ):
                    results[(lat, lon)] = 0 if is_integer else 0.0
                else:
                    results[(lat, lon)] = (
                        int(raw_val) if is_integer else float(raw_val)
                    )
    except Exception as e:
        print(f"Error sampling {raster_path}: {e}")

    return results


# --- BATCH EXTRACTORS ---


def get_elevation_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["elevation"], coords)


def get_slope_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["slope"], coords)


def get_aspect_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["aspect"], coords)


def get_curvature_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["curvature"], coords)


def get_twi_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["twi"], coords)


def get_spi_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["spi"], coords)


def get_roughness_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["roughness"], coords)


def get_ndvi_baseline_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["ndvi_baseline"], coords)


def get_lulc_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], int]:
    return sample_raster_batch(
        RASTER_PATHS["lulc"], coords, is_integer=True
    )


def get_soil_type_batch(
    coords: List[Tuple[float, float]]
) -> Dict[Tuple[float, float], int]:
    return sample_raster_batch(
        RASTER_PATHS["soil_type"], coords, is_integer=True
    )