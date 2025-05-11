-- Определение перечислений
DROP TYPE IF EXISTS zone_type CASCADE;
CREATE TYPE zone_type AS ENUM ('circle', 'rectangle', 'polygon');

DROP TYPE IF EXISTS sensor_type CASCADE;
-- Пример возможных типов сенсоров
CREATE TYPE sensor_type AS ENUM ('gps', 'temperature', 'pressure');

DROP TYPE IF EXISTS sensor_status CASCADE;
CREATE TYPE sensor_status AS ENUM ('ACTIVE', 'INACTIVE');

DROP TYPE IF EXISTS user_role CASCADE;
CREATE TYPE user_role AS ENUM ('admin', 'operator', 'analyst');

DROP TYPE IF EXISTS event_type CASCADE;
CREATE TYPE event_type AS ENUM ('move', 'stop', 'zone_entr', 'zone_exit', 'speed_limit', 'sensor_fault', 'other');

DROP TYPE IF EXISTS alert_type CASCADE;
CREATE TYPE alert_type AS ENUM ('zone_exit', 'zone_enter', 'speed_violation', 'sensor_failure', 'disconnection', 'custom');

DROP TYPE IF EXISTS alert_severity CASCADE;
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');

DROP TYPE IF EXISTS route_status CASCADE;
CREATE TYPE route_status AS ENUM ('planned', 'in_progress', 'completed', 'delayed', 'cancelled');

DROP TYPE IF EXISTS object_type CASCADE;
CREATE TYPE object_type AS ENUM ('vehicle', 'cargo', 'equipment', 'other');

CREATE EXTENSION IF NOT EXISTS postgis;

-- Таблица пользователей
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Таблица объектов
CREATE TABLE objects (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type object_type NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Таблица связи пользователей и объектов
CREATE TABLE userobjects (
    user_id VARCHAR(36) NOT NULL,
    object_id VARCHAR(36) NOT NULL,
    access_level VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, object_id),
    UNIQUE (user_id, object_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);

-- Таблица сенсоров
CREATE TABLE sensors (
    id VARCHAR(36) PRIMARY KEY,
    object_id VARCHAR(36) NOT NULL,
    type sensor_type NOT NULL,
    location VARCHAR(100),
    status sensor_status NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);

-- Таблица событий
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(36) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    speed FLOAT,
    event_type event_type NOT NULL,
    details VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- Таблица оповещений
CREATE TABLE alerts (
    id VARCHAR(36) PRIMARY KEY,
    event_id INTEGER NOT NULL,
    alert_type alert_type NOT NULL,
    severity alert_severity NOT NULL,
    message VARCHAR(500) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

-- Таблица зон
CREATE TABLE zones (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    zone_type zone_type NOT NULL,
    coordinates JSON NOT NULL,
    description VARCHAR(500),
    boundary_polygon Geometry(POLYGON, 4326) NOT NULL,
    center_point Geometry(POINT, 4326),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Таблица связи объектов и зон
CREATE TABLE objectzones (
    object_id VARCHAR(36) NOT NULL,
    zone_id VARCHAR(36) NOT NULL,
    entered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    exited_at TIMESTAMP,
    PRIMARY KEY (object_id, zone_id),
    FOREIGN KEY (object_id) REFERENCES objects(id),
    FOREIGN KEY (zone_id) REFERENCES zones(id)
);

-- Таблица маршрутов
CREATE TABLE routes (
    id VARCHAR(36) PRIMARY KEY,
    object_id VARCHAR(36) NOT NULL,
    name VARCHAR(100),
    description VARCHAR(500),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status route_status NOT NULL DEFAULT 'planned',
    points JSON NOT NULL,
    metadata JSON,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);

-- Таблица телеметрии
CREATE TABLE telemetry (
    id VARCHAR(36) PRIMARY KEY,
    object_id VARCHAR(36) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    signal_strength FLOAT,
    additional_metrics JSON,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);