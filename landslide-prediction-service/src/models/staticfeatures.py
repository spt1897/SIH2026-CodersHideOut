from pydantic import BaseModel

class StaticFeatures(BaseModel):
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
    soil_sand: float
    soil_silt: float
    soil_clay: float
    lithology_encoded: int