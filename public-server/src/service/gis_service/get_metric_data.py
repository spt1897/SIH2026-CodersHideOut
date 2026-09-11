import pandas as pd
import h3

DATASET_PATH = r"C:\Users\SAPTARSHI GHOSH\Desktop\data-1788945459489.csv"

# -------------------------------------------------------------------------
# BIN DEFINITIONS
# -------------------------------------------------------------------------

ELEVATION_BINS = [
    (0, 1600, "#2b83ba"),
    (1600, 1800, "#abdda4"),
    (1800, 2000, "#ffffbf"),
    (2000, 2300, "#fdae61"),
    (2300, None, "#d7191c")
]

SLOPE_BINS = [
    (0, 15, "#2b83ba"),
    (15, 25, "#abdda4"),
    (25, 35, "#ffffbf"),
    (35, 45, "#fdae61"),
    (45, None, "#d7191c")
]

TWI_BINS = [
    (0, 4.5, "#edf8fb"),
    (4.5, 5.5, "#b2e2e2"),
    (5.5, 7.0, "#66c2a4"),
    (7.0, 8.5, "#2ca25f"),
    (8.5, None, "#006d2c")
]

SPI_BINS = [
    (0, 10, "#f7fcf5"),
    (10, 30, "#bae4b3"),
    (30, 70, "#74c476"),
    (70, 120, "#31a354"),
    (120, None, "#006d2c")
]

VEGETATION_BINS = [
    (-1.0, 0.2, "#d73027"),
    (0.2, 0.4, "#fc8d59"),
    (0.4, 0.6, "#fee08b"),
    (0.6, 0.7, "#d9ef8b"),
    (0.7, 1.0, "#1a9850")
]

BUILDING_DENSITY_BINS = [
    (0, 0.05, "#f7f7f7"),
    (0.05, 0.20, "#cccccc"),
    (0.20, 0.50, "#969696"),
    (0.50, None, "#252525")
]

DRAINAGE_DENSITY_BINS = [
    (0, 0.15, "#eff3ff"),
    (0.15, 0.30, "#bdd7e7"),
    (0.30, 0.45, "#6baed6"),
    (0.45, None, "#2171b5")
]

ROAD_DENSITY_BINS = [
    (0, 0.1, "#f7f7f7"),
    (0.1, 2.0, "#fbb4ae"),
    (2.0, 10.0, "#b3cde3"),
    (10.0, None, "#ccebc5")
]


# -------------------------------------------------------------------------
# CORE HELPER FUNCTIONS
# -------------------------------------------------------------------------

def _classify_val(val: float, bin_definitions: list) -> tuple:
    for start, end, color in bin_definitions:
        if end is not None:
            if start <= val < end:
                return color, f"{start} - {end}"
        else:
            if val >= start:
                return color, f"{start}+"
    
    last_start, _, last_color = bin_definitions[-1]
    return last_color, f"{last_start}+"


def _format_legend_json(bin_definitions: list) -> list:
    """Formats bins into a standard JSON-serializable list of dicts."""
    legend = []
    for start, end, color in bin_definitions:
        label = f"{start} - {end}" if end is not None else f">{start}"
        legend.append({
            "min": start,
            "max": end,
            "color": color,
            "label": label
        })
    return legend


def _generate_feature_collection_with_legend(df: pd.DataFrame, column_name: str, param_name: str, bin_definitions: list) -> dict:
    features = []
    
    h3_indices = df['h3_index'].astype(str).tolist()
    values = df[column_name].astype(float).tolist()
    districts = df.get('district_names', pd.Series(['N/A'] * len(df))).tolist()
    sub_districts = df.get('sub_districts', pd.Series(['N/A'] * len(df))).tolist()

    for h3_idx, val, dist, sub_dist in zip(h3_indices, values, districts, sub_districts):
        fill_color, range_label = _classify_val(val, bin_definitions)
        
        boundary = h3.cell_to_boundary(h3_idx)
        coords = [[lng, lat] for lat, lng in boundary]
        coords.append(coords[0])

        feature = {
            "type": "Feature",
            "properties": {
                "h3_index": h3_idx,
                "parameter": param_name,
                "value": round(val, 4),
                "range_label": range_label,
                "fill_color": fill_color,
                "district": str(dist),
                "sub_district": str(sub_dist)
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }
        features.append(feature)

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    legend = _format_legend_json(bin_definitions)
    
    # Return as a clean JSON-serializable response payload
    return {
        "ranges": legend,
        "feature_collection": feature_collection
    }


# -------------------------------------------------------------------------
# GETTER FUNCTIONS
# -------------------------------------------------------------------------

def get_elevation_feature_collection(filepath: str = DATASET_PATH) -> dict:
    df = pd.read_csv(filepath)
    return _generate_feature_collection_with_legend(df, 'elevation_m', 'elevation', ELEVATION_BINS)

def get_slope_feature_collection(filepath: str = DATASET_PATH) -> dict:
    df = pd.read_csv(filepath)
    return _generate_feature_collection_with_legend(df, 'slope_deg', 'slope', SLOPE_BINS)

def get_twi_feature_collection(filepath: str = DATASET_PATH) -> dict:
    df = pd.read_csv(filepath)
    return _generate_feature_collection_with_legend(df, 'twi', 'twi', TWI_BINS)

def get_spi_feature_collection(filepath: str = DATASET_PATH) -> dict:
    df = pd.read_csv(filepath)
    return _generate_feature_collection_with_legend(df, 'spi', 'spi', SPI_BINS)

def get_vegetation_feature_collection(filepath: str = DATASET_PATH) -> dict:
    df = pd.read_csv(filepath)
    return _generate_feature_collection_with_legend(df, 'ndvi_baseline', 'vegetation', VEGETATION_BINS)

def get_building_density_feature_collection(filepath: str = DATASET_PATH) -> dict:
    df = pd.read_csv(filepath)
    return _generate_feature_collection_with_legend(df, 'building_density', 'building_density', BUILDING_DENSITY_BINS)

def get_drainage_density_feature_collection(filepath: str = DATASET_PATH) -> dict:
    df = pd.read_csv(filepath)
    return _generate_feature_collection_with_legend(df, 'drainage_density', 'drainage_density', DRAINAGE_DENSITY_BINS)

def get_road_density_feature_collection(filepath: str = DATASET_PATH) -> dict:
    df = pd.read_csv(filepath)
    return _generate_feature_collection_with_legend(df, 'road_density', 'road_density', ROAD_DENSITY_BINS)