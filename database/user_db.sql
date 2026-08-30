-- officials or admins
CREATE TABLE officials (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR NOT NULL UNIQUE,
    phno VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    role VARCHAR NOT NULL,
    designation VARCHAR NOT NULL,
    employee_id VARCHAR NOT NULL UNIQUE,
    agency VARCHAR NOT NULL,
    state_code VARCHAR NOT NULL,
    district_codes TEXT NOT NULL,
    h3_res6_cells TEXT NOT NULL
);

-- SQLAlchemy creates these indexes automatically based on index=True
CREATE INDEX ix_officials_id ON officials(id);
CREATE INDEX ix_officials_email ON officials(email);

-- For Citizens
CREATE TABLE citizens (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    phno VARCHAR NOT NULL UNIQUE,
    email VARCHAR UNIQUE,
    password VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'USER',
    h3_home_cell VARCHAR NOT NULL,
    preferred_language VARCHAR NOT NULL DEFAULT 'English'
);

-- SQLAlchemy creates these indexes automatically based on index=True
CREATE INDEX ix_citizens_id ON citizens(id);
CREATE INDEX ix_citizens_phno ON citizens(phno);
CREATE INDEX ix_citizens_h3_home_cell ON citizens(h3_home_cell);