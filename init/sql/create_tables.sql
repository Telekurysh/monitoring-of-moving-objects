-- Определение перечислений
CREATE TYPE zone_type AS ENUM ('CIRCLE', 'RECTANGLE', 'POLYGON');

CREATE TYPE sensor_type AS ENUM ('GPS', 'FUEL');

CREATE TYPE sensor_status AS ENUM ('ACTIVE', 'INACTIVE');

CREATE TYPE user_role AS ENUM ('ADMIN', 'OPERATOR', 'ANALYST');

CREATE TYPE event_type AS ENUM ('MOVE', 'STOP', 'ZONE_ENTER', 'ZONE_EXIT', 'SPEED_LIMIT', 'SENSOR_FAULT', 'OTHER');

CREATE TYPE alert_type AS ENUM ('ZONE_EXIT', 'ZONE_ENTER', 'SPEED_VIOLATION', 'SENSOR_FAILURE', 'DISCONNECTION', 'CUSTOM');

CREATE TYPE alert_severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

CREATE TYPE route_status AS ENUM ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'DELAYED', 'CANCELLED');

CREATE TYPE object_type AS ENUM ('VEHICLE', 'CARGO', 'EQUIPMENT', 'OTHER');

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица пользователей
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
CREATE TABLE objects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    object_type object_type NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Таблица связи пользователей и объектов
CREATE TABLE userobject (
    user_id UUID NOT NULL,
    object_id UUID NOT NULL,
    access_level VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, object_id),
    UNIQUE (user_id, object_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);

-- Таблица сенсоров
CREATE TABLE sensors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    object_id UUID NOT NULL,
    sensor_type sensor_type NOT NULL,
    location VARCHAR(100),
    sensor_status sensor_status NOT NULL DEFAULT 'ACTIVE',
    latitude FLOAT,
    longitude FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);

-- Таблица событий
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
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    object_id UUID NOT NULL,
    name VARCHAR(100),
    description VARCHAR(500),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status route_status NOT NULL DEFAULT 'PLANNED',
    points JSON NOT NULL,
    metadata JSON,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (object_id) REFERENCES objects(id)
);



-- Роль администратора: полный доступ ко всем таблицам
CREATE ROLE admin_user
WITH
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT LOGIN
    CONNECTION LIMIT -1 PASSWORD 'password_admin';
GRANT SELECT, INSERT, UPDATE, DELETE ON users, objects, userobject, sensors, events, alerts, zones, object_zone, routes TO admin_user;

-- Роль оператора: доступ к объектам, сенсорам, событиям, оповещениям, маршрутам
CREATE ROLE operator_user
WITH
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT LOGIN
    CONNECTION LIMIT -1 PASSWORD 'password_operator';
GRANT SELECT ON objects, sensors, events, alerts, routes TO operator_user;
GRANT INSERT, UPDATE ON events, alerts, routes TO operator_user;

-- Роль аналитика: только чтение по основным таблицам
CREATE ROLE analyst_user
WITH
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT LOGIN
    CONNECTION LIMIT -1 PASSWORD 'password_analyst';
GRANT SELECT ON objects, sensors, events, alerts, zones, routes TO analyst_user;

-- Функция-триггер для деактивации пользователя вместо удаления
CREATE OR REPLACE FUNCTION deactivate_user_instead_of_delete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users SET is_active = FALSE, updated_at = NOW() WHERE id = OLD.id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Триггер на удаление пользователя
CREATE TRIGGER trg_deactivate_user_instead_of_delete
BEFORE DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION deactivate_user_instead_of_delete();

-- Функция для обновления object_zone при изменении координат сенсора
CREATE OR REPLACE FUNCTION update_object_zone_on_sensor_change()
RETURNS TRIGGER AS $$
DECLARE
    sensor_point Geometry(POINT, 4326);
    zone_rec RECORD;
    v_object_id UUID;  -- изменено имя переменной
BEGIN
    -- Если координаты не заданы, ничего не делаем
    IF (NEW.latitude IS NULL OR NEW.longitude IS NULL) THEN
        RETURN NEW;
    END IF;

    -- Получаем объект, к которому привязан сенсор
    v_object_id := NEW.object_id;

    -- Создаём геометрию точки сенсора
    sensor_point := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);

    -- Для каждой зоны проверяем, находится ли сенсор внутри
    FOR zone_rec IN SELECT id FROM zones WHERE ST_Contains(boundary_polygon, sensor_point)
    LOOP
        -- Если уже есть активная запись object_zone, ничего не делаем
        IF EXISTS (
            SELECT 1 FROM object_zone
            WHERE object_id = v_object_id AND zone_id = zone_rec.id AND exited_at IS NULL
        ) THEN
            CONTINUE;
        END IF;

        -- Если была запись с exited_at, обновляем её (ре-энтри)
        IF EXISTS (
            SELECT 1 FROM object_zone
            WHERE object_id = v_object_id AND zone_id = zone_rec.id AND exited_at IS NOT NULL
        ) THEN
            UPDATE object_zone
            SET entered_at = NOW(), exited_at = NULL
            WHERE object_id = v_object_id AND zone_id = zone_rec.id;
        ELSE
            -- Иначе создаём новую запись
            INSERT INTO object_zone(object_id, zone_id, entered_at, exited_at)
            VALUES (v_object_id, zone_rec.id, NOW(), NULL)
            ON CONFLICT (object_id, zone_id) DO NOTHING;
        END IF;
    END LOOP;

    -- Теперь обработаем выход из зон: если были активные object_zone, но теперь сенсор вне зоны, ставим exited_at
    FOR zone_rec IN
        SELECT oz.zone_id FROM object_zone oz
        WHERE oz.object_id = v_object_id AND oz.exited_at IS NULL
        AND NOT EXISTS (
            SELECT 1 FROM zones z
            WHERE z.id = oz.zone_id AND ST_Contains(z.boundary_polygon, sensor_point)
        )
    LOOP
        UPDATE object_zone
        SET exited_at = NOW()
        WHERE object_id = v_object_id AND zone_id = zone_rec.zone_id AND exited_at IS NULL;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер на вставку и обновление координат сенсора
CREATE TRIGGER trg_update_object_zone_on_sensor_change
AFTER INSERT OR UPDATE OF latitude, longitude ON sensors
FOR EACH ROW
EXECUTE FUNCTION update_object_zone_on_sensor_change();
