-- 1. Streamlined Debris State Enum
CREATE TYPE debris_state_enum AS ENUM (
    'STABLE',
    'FLOWING',
    'DEPLETED',
    'DEPOSITED'
);

-- 2.  Simulation Cell State Table
CREATE TABLE IF NOT EXISTS simulation_cell_state (
    h3_index VARCHAR(15) PRIMARY KEY,

    -- GRAPH TOPOLOGY & TERRAIN
    downstream_neighbors TEXT[] NOT NULL DEFAULT '{}',
    elevation_m FLOAT NOT NULL,
    slope_degrees FLOAT NOT NULL,
    curvature FLOAT NOT NULL,             
    friction_coefficient FLOAT NOT NULL,  -- Pre-calculated mu_eff

    -- DISASTER ENGINE DUAL-STATE FLAG
    is_real_affected BOOLEAN NOT NULL DEFAULT FALSE, -- TRUE = Live Seismic Data | FALSE = AOT Forecast Layer
    debris_state debris_state_enum NOT NULL DEFAULT 'STABLE',

    -- AHEAD-OF-TIME (AOT) WORST-CASE UPPER BOUNDS (Active when is_real_affected = FALSE)
    min_arrival_time_seconds FLOAT NOT NULL DEFAULT 0.0, -- Earliest arrival timestamp
    max_velocity_ms FLOAT NOT NULL DEFAULT 0.0,          -- Peak flow speed
    max_debris_volume_m3 FLOAT NOT NULL DEFAULT 0.0,     -- Peak passing volume
    max_kinetic_energy_jkg FLOAT NOT NULL DEFAULT 0.0,   -- Peak specific kinetic energy
    max_impact_parameter FLOAT NOT NULL DEFAULT 0.0,     -- Peak dynamic impact pressure (rho * h * v^2)

    -- REAL-TIME LIVE SENSOR METRICS (Active when is_real_affected = TRUE)
    live_velocity_ms FLOAT NOT NULL DEFAULT 0.0,         -- Telemetry derived actual speed
    live_debris_volume_m3 FLOAT NOT NULL DEFAULT 0.0,    -- Telemetry derived actual volume
    live_impact_parameter FLOAT NOT NULL DEFAULT 0.0,    -- Dynamic live force vector

    -- INFRASTRUCTURE IMPACT & AUTOMATION
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,           -- True if max_impact or live_impact breaks road/bridge

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES FOR INSTANT MAPBOX / DECK.GL VIEWPORT FETCHES
-- Fast lookup for AOT forecast polygon
CREATE INDEX IF NOT EXISTS idx_sim_aot_extent ON simulation_cell_state(h3_index) 
    WHERE debris_state != 'STABLE' AND is_real_affected = FALSE;

-- Fast lookup for live emergency footprint (Pulsing Red)
CREATE INDEX IF NOT EXISTS idx_sim_live_affected ON simulation_cell_state(is_real_affected) 
    WHERE is_real_affected = TRUE;

-- Fast lookup for blocked infrastructure corridors
CREATE INDEX IF NOT EXISTS idx_sim_blocked_roads ON simulation_cell_state(is_blocked) 
    WHERE is_blocked = TRUE;