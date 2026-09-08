CREATE TYPE debris_state_enum AS ENUM (
    'STABLE',
    'FLOWING'
);

CREATE TABLE IF NOT EXISTS simulation_cell_state (
    h3_index VARCHAR(15) PRIMARY KEY,

    elevation FLOAT NOT NULL,

    friction_coefficient FLOAT NOT NULL,

    debris_state debris_state_enum NOT NULL DEFAULT 'STABLE',

    normalized_mass FLOAT NOT NULL DEFAULT 0.0,

    velocity FLOAT NOT NULL DEFAULT 0.0,

    specific_pe FLOAT NOT NULL DEFAULT 0.0,

    specific_ke FLOAT NOT NULL DEFAULT 0.0,

    arrival_time FLOAT NOT NULL DEFAULT -1.0,

    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,

    is_real_affected BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_sim_blocked
ON simulation_cell_state(is_blocked)
WHERE is_blocked = TRUE;

CREATE INDEX IF NOT EXISTS idx_sim_real_affected
ON simulation_cell_state(is_real_affected)
WHERE is_real_affected = TRUE;

CREATE INDEX IF NOT EXISTS idx_state_flowing
ON simulation_cell_state(debris_state)
WHERE debris_state = 'FLOWING';