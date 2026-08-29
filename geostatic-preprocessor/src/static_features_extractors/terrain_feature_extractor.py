import os
import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer
from typing import Callable, Tuple, List, Dict, Any, Union, Awaitable

# Ensure you have your configuration imported
from src.static_features_extractors.raster_file_config import RASTER_PATHS

# ==========================================
# 1. BATCH RASTER SAMPLING EXTRACTORS
# ==========================================

def sample_raster_batch(raster_path,coords):
    # coords is list of (lat, lon)
    lats = [c[0] for c in coords]
    lons = [c[1] for c in coords]
    
    # EXACTLY LIKE YOUR WORKING CODE: zip(lons, lats)
    pts_lon_lat = zip(lons, lats)
    
    with rasterio.open(raster_path) as src:
        sampled_vals = [val[0] for val in src.sample(pts_lon_lat)]
        
        cleaned_vals = [
            float(v) if (v is not None and v != src.nodata and not np.isnan(v)) else np.nan 
            for v in sampled_vals
        ]
        
    return dict(zip(coords, cleaned_vals))


def get_elevation_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["elevation"], coords)


def get_slope_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["slope"], coords)


def get_aspect_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["aspect"], coords)


def get_curvature_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["curvature"], coords)


def get_twi_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["twi"], coords)


def get_spi_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["spi"], coords)


def get_roughness_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["roughness"], coords)


def get_ndvi_baseline_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:
    return sample_raster_batch(RASTER_PATHS["ndvi_baseline"], coords)


def get_lulc_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], int]:
    return sample_raster_batch(RASTER_PATHS["lulc"], coords)


def get_soil_type_batch(coords: List[Tuple[float, float]]) -> Dict[Tuple[float, float], int]:
    return sample_raster_batch(RASTER_PATHS["soil_type"], coords)