-- Определение перечислений
DROP TYPE IF EXISTS zone_type CASCADE;
CREATE TYPE zone_type AS ENUM ('CIRCLE', 'RECTANGLE', 'POLYGON');

DROP TYPE IF EXISTS sensor_type CASCADE;
CREATE TYPE sensor_type AS ENUM ('GPS', 'FUEL');

DROP TYPE IF EXISTS sensor_status CASCADE;
CREATE TYPE sensor_status AS ENUM ('ACTIVE', 'INACTIVE');

DROP TYPE IF EXISTS user_role CASCADE;
CREATE TYPE user_role AS ENUM ('ADMIN', 'OPERATOR', 'ANALYST');

DROP TYPE IF EXISTS event_type CASCADE;
CREATE TYPE event_type AS ENUM ('MOVE', 'STOP', 'ZONE_ENTER', 'ZONE_EXIT', 'SPEED_LIMIT', 'SENSOR_FAULT', 'OTHER');

DROP TYPE IF EXISTS alert_type CASCADE;
CREATE TYPE alert_type AS ENUM ('ZONE_EXIT', 'ZONE_ENTER', 'SPEED_VIOLATION', 'SENSOR_FAILURE', 'DISCONNECTION', 'CUSTOM');

DROP TYPE IF EXISTS alert_severity CASCADE;
CREATE TYPE alert_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

DROP TYPE IF EXISTS route_status CASCADE;
CREATE TYPE route_status AS ENUM ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'DELAYED', 'CANCELLED');

DROP TYPE IF EXISTS object_type CASCADE;
CREATE TYPE object_type AS ENUM ('VEHICLE', 'CARGO', 'EQUIPMENT', 'OTHER');

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица пользователей
DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Таблица объектов
DROP TABLE IF EXISTS objects CASCADE;
CREATE TABLE objects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    object_type object_type NOT NULL, -- изменено с type на object_type
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Таблица связи пользователей и объектов
DROP TABLE IF EXISTS userobjects CASCADE;
CREATE TABLE userobjects (
    user_id UUID NOT NULL,
    object_id UUID NOT NULL,
    access_level VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, object_id),
    UNIQUE (user_id, object_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);

-- Таблица сенсоров
DROP TABLE IF EXISTS sensors CASCADE;
CREATE TABLE sensors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    object_id UUID NOT NULL,
    sensor_type sensor_type NOT NULL,  -- изменено: имя столбца
    location VARCHAR(100),
    sensor_status sensor_status NOT NULL DEFAULT 'ACTIVE',  -- изменено: имя столбца
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);

-- Таблица событий
DROP TABLE IF EXISTS events CASCADE;
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id UUID NOT NULL,
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
DROP TABLE IF EXISTS alerts CASCADE;
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL,
    alert_type alert_type NOT NULL,
    severity alert_severity NOT NULL,
    message VARCHAR(500) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (event_id) REFERENCES events(id)
);

-- Таблица зон
DROP TABLE IF EXISTS zones CASCADE;
CREATE TABLE zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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
DROP TABLE IF EXISTS object_zone CASCADE;
CREATE TABLE object_zone (
    object_id UUID NOT NULL,
    zone_id UUID NOT NULL,
    entered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    exited_at TIMESTAMP,
    PRIMARY KEY (object_id, zone_id),
    FOREIGN KEY (object_id) REFERENCES objects(id),
    FOREIGN KEY (zone_id) REFERENCES zones(id)
);

-- Таблица маршрутов
DROP TABLE IF EXISTS routes CASCADE;
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    object_id UUID NOT NULL,
    name VARCHAR(100),
    description VARCHAR(500),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status route_status NOT NULL DEFAULT 'PLANNED', -- исправлено значение по умолчанию
    points JSON NOT NULL,
    metadata JSON,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);

-- Таблица телеметрии
DROP TABLE IF EXISTS telemetry CASCADE;
CREATE TABLE telemetry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    object_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    signal_strength FLOAT,
    additional_metrics JSON,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);