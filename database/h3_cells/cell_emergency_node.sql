CREATE TABLE IF NOT EXISTS cell_emergency_nodes (
    h3_index VARCHAR(15) PRIMARY KEY REFERENCES prediction_parameters(h3_index) ON DELETE CASCADE,

    -- POLICE STATIONS: Parallel arrays for names, contacts, distances, and native Point geometries
    police_names TEXT[],
    police_points GEOMETRY(Point, 4326)[],
    police_distances_km FLOAT[],
    police_contacts TEXT[],

    -- FIRE STATIONS
    fire_names TEXT[],
    fire_points GEOMETRY(Point, 4326)[],
    fire_distances_km FLOAT[],
    fire_contacts TEXT[],

    -- HOSPITALS
    hospital_names TEXT[],
    hospital_points GEOMETRY(Point, 4326)[],
    hospital_distances_km FLOAT[],
    hospital_contacts TEXT[],

    -- TRAFFIC BOOTHS
    traffic_booth_names TEXT[],
    traffic_booth_points GEOMETRY(Point, 4326)[],
    traffic_booth_distances_km FLOAT[],
    traffic_booth_contacts TEXT[],

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);