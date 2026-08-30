from pydantic import BaseModel

class RealtimeParameters(BaseModel):
    h3_index:str
    rainfall_1h_mm :float
    rainfall_3h_mm  :float
    rainfall_24h_mm :float
    rainfall_3d_mm :float
    rainfall_7d_mm :float
    soil_moisture :float
    earthquake_count_7d :float
    earthquake_count_30d  :float
    max_earthquake_magnitude :float
    distance_to_recent_earthquake_m :float