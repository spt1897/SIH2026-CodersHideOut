import os
from typing import Callable, Dict, List, Tuple, Any, Union
import h3
import numpy as np
import pandas as pd
import pyproj
import rasterio
import inspect

def coord_to_h3_aggregate(
    bbox: Tuple[float, float, float, float],
    grid_resolution_deg: float,
    extractor_func: Callable[[List[Tuple[float, float]]], Dict[Tuple[float, float], Union[float, int, Dict[str, Union[float, int]]]]],
    parameter_name: str,
    h3_resolution: int = 9,
    agg_strategy: str = 'auto'
) -> Tuple[List[Tuple], str]:
    min_lat, min_lon, max_lat, max_lon = bbox

    # 1. Generate lattice of lat/lon points inside bounding box
    lat_steps = np.arange(min_lat, max_lat, grid_resolution_deg)
    lon_steps = np.arange(min_lon, max_lon, grid_resolution_deg)
    
    if len(lat_steps) == 0: lat_steps = np.array([min_lat])
    if len(lon_steps) == 0: lon_steps = np.array([min_lon])

    lats, lons = np.meshgrid(lat_steps, lon_steps, indexing='ij')
    flat_lats = lats.flatten()
    flat_lons = lons.flatten()
    coords = list(zip(flat_lats, flat_lons))

    if not coords:
        return [], ""

    try:
        # Check if the extractor accepts a 'bbox' parameter
        sig = inspect.signature(extractor_func)
        if 'bbox' in sig.parameters:
            raw_sampled_dict = extractor_func(coords, bbox=bbox)
        else:
            raw_sampled_dict = extractor_func(coords)
    except TypeError:
        # Fallback attempt
        try:
            raw_sampled_dict = extractor_func(coords, bbox)
        except TypeError:
            raw_sampled_dict = extractor_func(coords)
        if not raw_sampled_dict:
            return [], ""

    # 3. Build DataFrame
    records_list = []
    
    # Check structure of values returned
    sample_val = next(iter(raw_sampled_dict.values()))
    
    if isinstance(sample_val, dict):
        target_columns = list(sample_val.keys())
        for (lat, lon) in coords:
            val_dict = raw_sampled_dict.get((lat, lon), {})
            row = {'latitude': float(lat), 'longitude': float(lon)}
            row.update(val_dict)
            records_list.append(row)
    else:
        target_columns = [parameter_name]
        for (lat, lon), val in raw_sampled_dict.items():
            records_list.append({'latitude': float(lat), 'longitude': float(lon), parameter_name: val})

    df = pd.DataFrame(records_list)

    # Convert all extracted parameter columns safely to numeric
    for col in target_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 4. Map lat/lon points to H3 Cell Index (Supports both H3 v3 and v4 API)
    if hasattr(h3, 'latlng_to_cell'):
        df['h3_index'] = [
            h3.latlng_to_cell(lat, lon, h3_resolution) 
            for lat, lon in zip(df['latitude'], df['longitude'])
        ]
    else:
        df['h3_index'] = [
            h3.geo_to_h3(lat, lon, h3_resolution) 
            for lat, lon in zip(df['latitude'], df['longitude'])
        ]

    # Helper function for statistical Mode
    def get_mode(series: pd.Series):
        valid_series = series.dropna()
        if valid_series.empty:
            return np.nan
        return valid_series.mode().iloc[0]

    # 5. Determine Aggregation Strategy per column
    agg_dict = {}
    categorical_params = {'lulc', 'soil_type', 'lithology_encoded'}
    proximity_params = {'distance_to_fault_m', 'distance_to_road_m', 'distance_to_river_m'}

    for col in target_columns:
        if agg_strategy == 'auto':
            if col in categorical_params:
                agg_dict[col] = get_mode
            elif col in proximity_params:
                agg_dict[col] = 'min'
            else:
                agg_dict[col] = 'mean'
        elif agg_strategy == 'mode':
            agg_dict[col] = get_mode
        elif agg_strategy == 'min':
            agg_dict[col] = 'min'
        else:
            agg_dict[col] = 'mean'

    # 6. Group by H3 Cell Index and aggregate
    aggregated_df = df.groupby('h3_index', as_index=False).agg(agg_dict)
    
    # Explicitly cast ONLY specific categorical integer columns
    for col in target_columns:
        if col in categorical_params:
            aggregated_df[col] = aggregated_df[col].fillna(0).round().astype(int)

    records = aggregated_df.to_dict(orient='records')

    # 7. Dynamic SQL UPSERT query
    cols_str = ", ".join(target_columns)
    placeholders_str = ", ".join([f"${i+2}" for i in range(len(target_columns))])
    update_assignments = ", ".join([f"{col} = EXCLUDED.{col}" for col in target_columns])

    query = f"""
        INSERT INTO prediction_parameters (h3_index, {cols_str})
        VALUES ($1, {placeholders_str})
        ON CONFLICT (h3_index) 
        DO UPDATE SET 
            {update_assignments},
            static_parameter_updated = CURRENT_TIMESTAMP;
    """

    tuple_data = []
    for rec in records:
        row_tuple = [str(rec['h3_index'])]
        for col in target_columns:
            val = rec[col]
            if pd.isna(val):
                row_tuple.append(None)
            elif isinstance(val, (int, np.integer)):
                row_tuple.append(int(val))
            elif isinstance(val, (float, np.floating)):
                row_tuple.append(float(val))
            else:
                row_tuple.append(val)
        tuple_data.append(tuple(row_tuple))

    return tuple_data, query
