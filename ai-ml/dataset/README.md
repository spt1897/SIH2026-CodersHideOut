## Datasets for North East India Landslide prediction model  
  
**Key Features:**  
1) 706 Real historical landslide events across NE India.
2) 705 Negative samples (Non-landslide events).
3) Total data  = 1411
4) Predicts Landslide based on 29 real world parameters:

-static/terrain/human-infra related parameters:
elevation_m
slope_deg
aspect_deg
curvature
twi
spi
roughness
lithology
soil_type
soil_sand
soil_silt
soil_silt
distance_to_fault_m
distance_to_road_m
distance_to_river_m
drainage_density
building_density
ndvi_baseline
lulc

-dynamic/trigerring parameters:
rainfall_1h_mm
rainfall_3h_mm
rainfall_24h_mm
rainfall_3d_mm
rainfall_7d_mm
soil_moisture
earthquake_count_7d
earthquake_count_30d
max_earthquake_magnitude
distance_to_recent_earthquake_m

Label = 1 (Landslide)
Label = 0 (No Landslide)