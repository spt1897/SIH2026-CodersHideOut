CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS cell_landmark_mapping (
    h3_index VARCHAR(15) PRIMARY KEY REFERENCES prediction_parameters(h3_index) ON DELETE CASCADE,

    -- ADMINISTRATIVE ARRAYS (Handles multi-district/state/town border cells)
    state_names TEXT[] NOT NULL,                  
    district_names TEXT[] NOT NULL,               
    sub_districts TEXT[],                          
    cities_towns TEXT[],                          
    localities_villages TEXT[],                   

    -- INFRASTRUCTURE & HYDRO ID ARRAYS (Intersecting exact cell region)
    road_ids BIGINT[],                          -- Array of OpenStreetMap Road IDs
    railway_ids BIGINT[],                       -- Array of Railway IDs
    river_ids BIGINT[],                         -- Array of River/Stream IDs
    powerline_ids BIGINT[],                     -- Array of Power Grid Line IDs
    waterline_ids BIGINT[],                     -- Array of Water Pipeline IDs
    telecom_ids BIGINT[],                       -- Array of Telecom Line IDs
    oilline_ids BIGINT[],                       -- Array of Oil/Gas Pipeline IDs

    -- LAND USE & LANDMARKS
    is_farmland BOOLEAN NOT NULL DEFAULT FALSE,
    agricultural_centroids GEOMETRY(MultiPoint, 4326),
    population_density FLOAT NOT NULL DEFAULT 0,
    estimated_population INT NOT NULL DEFAULT 0,
    building_density FLOAT NOT NULL DEFAULT 0,
    road_density FLOAT NOT NULL DEFAULT 0,
    railway_density FLOAT NOT NULL DEFAULT 0,
    landmark_names TEXT[],                       -- e.g. ARRAY['Viewpoint Alpha', 'Tea Estate Beta']

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spatial and Array Indexes
CREATE INDEX IF NOT EXISTS idx_cell_road_ids ON cell_landmark_mapping USING GIN (road_ids);
CREATE INDEX IF NOT EXISTS idx_cell_railway_ids ON cell_landmark_mapping USING GIN (railway_ids);
CREATE INDEX IF NOT EXISTS idx_cell_river_ids ON cell_landmark_mapping USING GIN (river_ids);
CREATE INDEX IF NOT EXISTS idx_cell_powerline_ids ON cell_landmark_mapping USING GIN (powerline_ids);
CREATE INDEX IF NOT EXISTS idx_cell_waterline_ids ON cell_landmark_mapping USING GIN (waterline_ids);
CREATE INDEX IF NOT EXISTS idx_cell_telecom_ids ON cell_landmark_mapping USING GIN (telecom_ids);
CREATE INDEX IF NOT EXISTS idx_cell_oilline_ids ON cell_landmark_mapping USING GIN (oilline_ids);