import inspect

from typing import Callable, List, Tuple

import h3
import numpy as np
import pandas as pd


def coord_to_h3_aggregate(
    bbox: Tuple[float, float, float, float],
    extractor_func: Callable,
    parameter_name: str,
    h3_resolution: int = 9,
    grid_resolution_deg:float = 0,
    agg_strategy: str = 'auto'
) -> Tuple[List[Tuple], str]:

    min_lat, min_lon, max_lat, max_lon = bbox

    # ============================================================
    # 1. Generate H3 cells directly from the bounding box
    # ============================================================

    poly = h3.LatLngPoly([
        (min_lat, min_lon),
        (min_lat, max_lon),
        (max_lat, max_lon),
        (max_lat, min_lon)
    ])

    h3_cells = list(
        h3.polygon_to_cells(
            poly,
            res=h3_resolution
        )
    )

    if not h3_cells:
        return [], ""

    # ============================================================
    # 2. Get center coordinates of every H3 cell
    # ============================================================

    coords = [
        h3.cell_to_latlng(h3_index)
        for h3_index in h3_cells
    ]

    if not coords:
        return [], ""

    # ============================================================
    # 3. Run extractor
    # ============================================================

    try:

        sig = inspect.signature(extractor_func)

        if 'bbox' in sig.parameters:

            raw_sampled_dict = extractor_func(
                coords,
                bbox=bbox
            )

        else:

            raw_sampled_dict = extractor_func(
                coords
            )

    except TypeError:

        # Fallback for extractors that accept bbox positionally
        try:

            raw_sampled_dict = extractor_func(
                coords,
                bbox
            )

        except TypeError:

            raw_sampled_dict = extractor_func(
                coords
            )

    if not raw_sampled_dict:
        return [], ""

    # ============================================================
    # 4. Build DataFrame
    # ============================================================

    records_list = []

    sample_val = next(
        iter(raw_sampled_dict.values())
    )

    # ------------------------------------------------------------
    # Extractor returns:
    # {
    #     (lat, lon): {
    #         "elevation_m": ...,
    #         "slope_deg": ...,
    #         ...
    #     }
    # }
    # ------------------------------------------------------------

    if isinstance(sample_val, dict):

        target_columns = list(
            sample_val.keys()
        )

        for h3_index, (lat, lon) in zip(
            h3_cells,
            coords
        ):

            val_dict = raw_sampled_dict.get(
                (lat, lon),
                {}
            )

            row = {
                'latitude': float(lat),
                'longitude': float(lon),
                'h3_index': h3_index
            }

            row.update(val_dict)

            records_list.append(row)

    # ------------------------------------------------------------
    # Extractor returns:
    # {
    #     (lat, lon): value
    # }
    # ------------------------------------------------------------

    else:

        target_columns = [
            parameter_name
        ]

        for h3_index, (lat, lon) in zip(
            h3_cells,
            coords
        ):

            val = raw_sampled_dict.get(
                (lat, lon),
                np.nan
            )

            records_list.append({
                'latitude': float(lat),
                'longitude': float(lon),
                'h3_index': h3_index,
                parameter_name: val
            })

    # ============================================================
    # 5. Create DataFrame
    # ============================================================

    df = pd.DataFrame(
        records_list
    )

    if df.empty:
        return [], ""

    # ============================================================
    # 6. Convert extracted parameters to numeric
    # ============================================================

    for col in target_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors='coerce'
            )

    # ============================================================
    # 7. Helper function for statistical mode
    # ============================================================

    def get_mode(
        series: pd.Series
    ):

        valid_series = series.dropna()

        if valid_series.empty:
            return np.nan

        return valid_series.mode().iloc[0]

    # ============================================================
    # 8. Determine aggregation strategy
    # ============================================================

    agg_dict = {}

    categorical_params = {
        'lulc',
        'soil_type',
        'lithology_encoded'
    }

    proximity_params = {
        'distance_to_fault_m',
        'distance_to_road_m',
        'distance_to_river_m'
    }

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

    # ============================================================
    # 9. Aggregate by H3 cell
    # ============================================================
    #
    # Since we now sample exactly once at each H3 cell center,
    # there normally won't be multiple rows per H3 cell.
    #
    # Keeping the groupby is useful for compatibility and allows
    # multiple samples per cell if an extractor is changed later.
    # ============================================================

    aggregated_df = (
        df
        .groupby(
            'h3_index',
            as_index=False
        )
        .agg(agg_dict)
    )

    # ============================================================
    # 10. Handle categorical parameters
    # ============================================================

    for col in target_columns:

        if col in categorical_params:

            aggregated_df[col] = (
                aggregated_df[col]
                .fillna(0)
                .round()
                .astype(int)
            )

    # ============================================================
    # 11. Convert DataFrame to records
    # ============================================================

    records = aggregated_df.to_dict(
        orient='records'
    )

    if not records:
        return [], ""

    # ============================================================
    # 12. Build dynamic SQL UPSERT query
    # ============================================================

    cols_str = ", ".join(
        target_columns
    )

    placeholders_str = ", ".join(
        f"${i + 2}"
        for i in range(
            len(target_columns)
        )
    )

    update_assignments = ", ".join(
        f"{col} = EXCLUDED.{col}"
        for col in target_columns
    )

    query = f"""
        INSERT INTO prediction_parameters (
            h3_index,
            {cols_str}
        )
        VALUES (
            $1,
            {placeholders_str}
        )
        ON CONFLICT (h3_index)
        DO UPDATE SET
            {update_assignments},
            static_parameter_updated = CURRENT_TIMESTAMP;
    """.strip()

    # ============================================================
    # 13. Build asyncpg executemany values
    # ============================================================

    tuple_data = []

    for rec in records:

        row_tuple = [
            str(rec['h3_index'])
        ]

        for col in target_columns:

            val = rec[col]

            # NaN / NaT -> PostgreSQL NULL
            if pd.isna(val):

                row_tuple.append(None)

            # NumPy / Python integers
            elif isinstance(
                val,
                (int, np.integer)
            ):

                row_tuple.append(
                    int(val)
                )

            # NumPy / Python floats
            elif isinstance(
                val,
                (float, np.floating)
            ):

                row_tuple.append(
                    float(val)
                )

            else:

                row_tuple.append(
                    val
                )

        tuple_data.append(
            tuple(row_tuple)
        )

    # ============================================================
    # 14. Return asyncpg payload
    # ============================================================

    return tuple_data, query