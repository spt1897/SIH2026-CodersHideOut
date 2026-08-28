import h3
import numpy as np
import pandas as pd
import asyncpg
from typing import Callable, Tuple, List, Dict, Any, Union, Awaitable

def coord_to_h3_aggregate(
    bbox: Tuple[float, float, float, float],
    grid_resolution_deg: float,
    extractor_func: Callable[[List[Tuple[float, float]]], Dict[Tuple[float, float], Union[float, int, Dict[str, Union[float, int]]]]],
    parameter_name: str,
    h3_resolution: int = 9,
    agg_strategy: str = 'auto'
) -> Tuple[List[Dict[str, Any]], Callable[[asyncpg.Connection], Awaitable[int]]]:
    """
    1. Generates lat/lon grid points within a bounding box tile.
    2. Calls your batch extractor function: extractor_func(coords) -> Dict[(lat, lon), val or Dict].
    3. Unpacks single vs multi-column returns (e.g. soil texture returning sand, silt, clay).
    4. Aggregates values per H3 cell using mean, mode, or min.
    5. Returns aggregated records AND an async DB operation function compatible with your DB wrapper.
    """
    min_lat, min_lon, max_lat, max_lon = bbox

    # 1. Generate lattice of lat/lon points inside the bounding box
    lat_steps = np.arange(min_lat, max_lat, grid_resolution_deg)
    lon_steps = np.arange(min_lon, max_lon, grid_resolution_deg)
    
    if len(lat_steps) == 0: lat_steps = np.array([min_lat])
    if len(lon_steps) == 0: lon_steps = np.array([min_lon])

    lats, lons = np.meshgrid(lat_steps, lon_steps)
    coords = list(zip(lats.flatten(), lons.flatten()))

    if not coords:
        async def noop_db_op(conn: asyncpg.Connection) -> int:
            return 0
        return [], noop_db_op

    # 2. Call batch extractor (Dict[(lat, lon) -> scalar OR dict])
    raw_sampled_dict = extractor_func(coords)

    if not raw_sampled_dict:
        async def noop_db_op(conn: asyncpg.Connection) -> int:
            return 0
        return [], noop_db_op

    # 3. Build DataFrame: unpack single vs multi-column dictionary returns
    records_list = []
    first_val = next(iter(raw_sampled_dict.values()))
    
    if isinstance(first_val, dict):
        target_columns = list(first_val.keys())
        for (lat, lon), val_dict in raw_sampled_dict.items():
            row = {'latitude': lat, 'longitude': lon}
            row.update(val_dict)
            records_list.append(row)
    else:
        target_columns = [parameter_name]
        for (lat, lon), val in raw_sampled_dict.items():
            records_list.append({'latitude': lat, 'longitude': lon, parameter_name: val})

    df = pd.DataFrame(records_list)

    # 4. Map lat/lon points to H3 Cell Index
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

    # 5. Route aggregation strategy for your complete static parameter list
    agg_dict = {}
    for col in target_columns:
        if agg_strategy == 'auto':
            # Categorical / discrete parameters -> MODE
            categorical_params = {
                'lulc', 
                'soil_type', 
                'lithology_encoded'
            }
            
            # Proximity / distance parameters -> MIN
            proximity_params = {
                'distance_to_fault_m', 
                'distance_to_road_m', 
                'distance_to_river_m'
            }
            
            # Continuous spatial parameters -> MEAN
            # (elevation_m, slope_deg, aspect_deg, curvature, twi, spi, roughness,
            #  soil_sand, soil_silt, soil_clay, drainage_density, building_density, ndvi_baseline)
            
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

    # 6. Group by H3 Cell Index and aggregate target columns
    aggregated_df = df.groupby('h3_index', as_index=False).agg(agg_dict)
    
    # Cast discrete integer features back to native Python ints
    integer_cols = {'lulc', 'soil_type', 'lithology_encoded'}
    for col in target_columns:
        if col in integer_cols or col.startswith('soil_'):
            aggregated_df[col] = aggregated_df[col].round().astype(int)

    records = aggregated_df.to_dict(orient='records')

    # 7. Construct dynamic SQL UPSERT query targeting prediction_parameters
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

    tuple_data = [
        tuple([rec['h3_index']] + [
            float(rec[col]) if isinstance(rec[col], (float, np.floating)) else int(rec[col])
            for col in target_columns
        ])
        for rec in records
    ]

    # 8. Async callable for database connection wrapper
    async def db_upsert_op(conn: asyncpg.Connection) -> int:
        if not tuple_data:
            return 0
        await conn.executemany(query, tuple_data)
        return len(tuple_data)

    return records, db_upsert_op