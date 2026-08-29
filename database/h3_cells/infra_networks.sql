CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- 1. TRANSPORTATION NETWORKS
-- ============================================================================

-- A. Roadways Network
CREATE TABLE IF NOT EXISTS roads (
    road_id BIGINT PRIMARY KEY,                 -- OSM Way ID / Unique Road ID
    name VARCHAR(255),                          -- Highway / Road Name
    geom GEOMETRY(LineString, 4326) NOT NULL,   -- Spatial Line Geometry (WGS84)
    
    -- DYNAMIC STATUS & AUDIT
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,  -- True if severed/blocked by landslide/disaster
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_roads_geom ON roads USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_roads_blocked ON roads(is_blocked) WHERE is_blocked = TRUE;


-- B. Railways Network
CREATE TABLE IF NOT EXISTS railways (
    railway_id BIGINT PRIMARY KEY,              -- OSM / OpenInfra Rail ID
    name VARCHAR(255),                          -- Railway Line / Route Name
    geom GEOMETRY(LineString, 4326) NOT NULL,
    
    -- DYNAMIC STATUS & AUDIT
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_railways_geom ON railways USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_railways_blocked ON railways(is_blocked) WHERE is_blocked = TRUE;


-- ============================================================================
-- 2. HYDROGRAPHY / WATERWAYS
-- ============================================================================

-- C. Rivers & Watercourses Network
CREATE TABLE IF NOT EXISTS rivers (
    river_id BIGINT PRIMARY KEY,                -- OSM Way ID / HydroSHEDS ID
    name VARCHAR(255),                          -- River / Canal / Stream Name
    geom GEOMETRY(LineString, 4326) NOT NULL,
    
    -- DYNAMIC STATUS & AUDIT
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,  -- True if dammed/blocked by debris or dam failure
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_rivers_geom ON rivers USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_rivers_blocked ON rivers(is_blocked) WHERE is_blocked = TRUE;


-- ============================================================================
-- 3. UTILITY & ENERGY PIPELINES / LINES
-- ============================================================================

-- D. Power Lines Grid Network
CREATE TABLE IF NOT EXISTS powerlines (
    powerline_id BIGINT PRIMARY KEY,            -- OpenInfra / OSM Power Relation ID
    name VARCHAR(255),                          -- Line Name / Circuit Identifier
    geom GEOMETRY(LineString, 4326) NOT NULL,
    
    -- DYNAMIC STATUS & AUDIT
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,  -- True if line/cable is snapped/down
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_powerlines_geom ON powerlines USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_powerlines_blocked ON powerlines(is_blocked) WHERE is_blocked = TRUE;


-- E. Water Supply Lines & Aqueducts
CREATE TABLE IF NOT EXISTS waterlines (
    waterline_id BIGINT PRIMARY KEY,            -- OpenInfra Pipeline ID
    name VARCHAR(255),                          -- Pipeline / Main Name
    geom GEOMETRY(LineString, 4326) NOT NULL,
    
    -- DYNAMIC STATUS & AUDIT
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,  -- True if pipe severed or burst
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_waterlines_geom ON waterlines USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_waterlines_blocked ON waterlines(is_blocked) WHERE is_blocked = TRUE;


-- F. Telecommunication Lines Grid
CREATE TABLE IF NOT EXISTS telecom (
    telecom_id BIGINT PRIMARY KEY,              -- Telecom Cable / Trunk Line ID
    name VARCHAR(255),                          -- Fiber/Trunk Line Name
    geom GEOMETRY(LineString, 4326) NOT NULL,
    
    -- DYNAMIC STATUS & AUDIT
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,  -- True if fiber/cable cut
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_telecom_geom ON telecom USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_telecom_blocked ON telecom(is_blocked) WHERE is_blocked = TRUE;


-- G. Oil & Gas Pipelines Network
CREATE TABLE IF NOT EXISTS oillines (
    oilline_id BIGINT PRIMARY KEY,              -- OpenInfra Pipeline ID
    name VARCHAR(255),                          -- Pipeline Identifier Name
    substance VARCHAR(50),                      -- oil, gas, crude, petrol
    geom GEOMETRY(LineString, 4326) NOT NULL,
    
    -- DYNAMIC STATUS & AUDIT
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,  -- True if pipeline ruptured/shut down
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_oillines_geom ON oillines USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_oillines_blocked ON oillines(is_blocked) WHERE is_blocked = TRUE;