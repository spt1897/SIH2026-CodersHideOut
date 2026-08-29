CREATE EXTENSION IF NOT EXISTS postgis;

-- Core H3 Spatial Cells Reference & Feature Map Table
CREATE TABLE IF NOT EXISTS prediction_parameters (
    -- SPATIAL IDENTIFIER
    h3_index VARCHAR(15) PRIMARY KEY,              -- Resolution 9 H3 Hexagon Index.

    -- STATIC TERRAIN PARAMETERS (Static - From Rasters)
    elevation_m FLOAT NOT NULL,                    
    slope_deg FLOAT NOT NULL,                      
    aspect_deg FLOAT,                              
    lithology_encoded INT NOT NULL DEFAULT 2,        
    curvature FLOAT NOT NULL,
    twi FLOAT NOT NULL,
    spi FLOAT NOT NULL,
    roughness FLOAT NOT NULL,   
    soil_type INT NOT NULL,
    soil_sand INT NOT NULL,
    soil_silt INT NOT NULL,
    soil_clay INT NOT NULL,
    distance_to_fault_m FLOAT NOT NULL,
    distance_to_road_m FLOAT NOT NULL,
    distance_to_river_m FLOAT NOT NULL,
    drainage_density FLOAT NOT NULL,
    building_density FLOAT NOT NULL,
    ndvi_baseline FLOAT NOT NULL,
    lulc INT NOT NULL,

    --DYNAMIC PARAMETERS
    rainfall_1h_mm FLOAT NOT NULL DEFAULT 0,
    rainfall_3h_mm  FLOAT NOT NULL DEFAULT 0,
    rainfall_24h_mm FLOAT NOT NULL DEFAULT 0,
    rainfall_3d_mm FLOAT NOT NULL DEFAULT 0,
    rainfall_7d_mm FLOAT NOT NULL DEFAULT 0,
    soil_moisture FLOAT NOT NULL,
    earthquake_count_7d FLOAT NOT NULL DEFAULT 0,
    earthquake_count_30d  FLOAT NOT NULL DEFAULT 0,
    max_earthquake_magnitude FLOAT NOT NULL DEFAULT 0,
    distance_to_recent_earthquake_m FLOAT NOT NULL DEFAULT 0,

    landslide_probability FLOAT DEFAULT 0,


    -- AUDIT TIMESTAMPS
    static_parameter_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dynamic_paramter_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_landslide_cells
ON prediction_parameters(landslide_probability)
WHERE landslide_probability > 0.5;