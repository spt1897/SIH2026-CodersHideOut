-- Main User database for auth
CREATE TABLE user_data (
    id INTEGER NOT NULL,
    agency VARCHAR(255),
    created_at TIMESTAMP(6),
    designation VARCHAR(255),
    district_codes TEXT,
    email VARCHAR(255) NOT NULL,
    employee_id VARCHAR(255),
    h3_res6_cells TEXT,
    last_login TIMESTAMP(6),
    name VARCHAR(255),
    password VARCHAR(255),
    phno VARCHAR(255),
    preferred_language VARCHAR(255),
    role VARCHAR(255),
    state_code VARCHAR(255),
    PRIMARY KEY (id),
    CONSTRAINT ukdhxuydjj5l1vds6s9eex23dcr UNIQUE (email),
    CONSTRAINT ukl14rs1kjduysd1kuflase5y43 UNIQUE (employee_id)
);

-- refresh token db
CREATE TABLE refreshtoken (
    user_id INTEGER NOT NULL,
    token VARCHAR(255),
    PRIMARY KEY (user_id)
);

-- extra releted to user_data
CREATE SEQUENCE user_data_seq START WITH 1 INCREMENT BY 50;