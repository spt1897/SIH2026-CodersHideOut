from pydantic import BaseModel


class Features(BaseModel):
    elevation_m: float
    slope_deg: float
    aspect_deg: float
    curvature: float
    twi: float
    spi: float
    roughness: float
    soil_type: float
    distance_to_fault_m: float
    distance_to_road_m: float
    distance_to_river_m: float
    drainage_density: float
    building_density: float
    ndvi_baseline: float
    lulc: float

    rainfall_1h_mm: float
    rainfall_3h_mm: float
    rainfall_24h_mm: float
    rainfall_3d_mm: float
    rainfall_7d_mm: float
    soil_moisture: float
    earthquake_count_7d: float
    earthquake_count_30d: float
    max_earthquake_magnitude: float
    distance_to_recent_earthquake_m: float

    soil_sand: float
    soil_silt: float
    soil_clay: float
    lithology_encoded: int