-- Включаем расширение для генерации UUID (если не установлено)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Удаляем и создаем таблицы в правильном порядке с учетом зависимостей

-- Таблица Alerts (удаляем первой из-за зависимостей)
DROP TABLE IF EXISTS alerts CASCADE;

-- Таблица ObjectZones
DROP TABLE IF EXISTS objectzones CASCADE;

-- Таблица UserObject
DROP TABLE IF EXISTS userobject CASCADE;

-- Таблица Routes
DROP TABLE IF EXISTS routes CASCADE;

-- Таблица Telemetry
DROP TABLE IF EXISTS telemetry CASCADE;

-- Таблица Events
DROP TABLE IF EXISTS events CASCADE;

-- Таблица Sensors
DROP TABLE IF EXISTS sensors CASCADE;

-- Таблица Zones
DROP TABLE IF EXISTS zones CASCADE;

-- Таблица Users
DROP TABLE IF EXISTS users CASCADE;

-- Таблица Objects (удаляем последней из-за ссылок на нее)
DROP TABLE IF EXISTS objects CASCADE;

-- Теперь создаем таблицы в правильном порядке

-- Таблица Objects
CREATE TABLE objects (
                         id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                         name TEXT NOT NULL,
                         type TEXT NOT NULL,
                         created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Таблица Users
CREATE TABLE users (
                       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                       username VARCHAR(50) UNIQUE NOT NULL,
                       email VARCHAR(255) UNIQUE NOT NULL,
                       password_hash TEXT NOT NULL,
                       role TEXT NOT NULL,
                       is_active BOOLEAN NOT NULL DEFAULT TRUE,
                       created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                       updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Таблица Zones
CREATE TABLE zones (
                       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                       name TEXT NOT NULL,
                       boundary_coordinates JSONB NOT NULL,
                       zone_type TEXT NOT NULL
);

-- Таблица Sensors
CREATE TABLE sensors (
                         id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                         object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
                         type TEXT NOT NULL,
                         location TEXT NOT NULL,
                         status TEXT NOT NULL,
                         installed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Таблица Events
CREATE TABLE events (
                        id SERIAL PRIMARY KEY,
                        sensor_id UUID NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        latitude DOUBLE PRECISION NOT NULL,
                        longitude DOUBLE PRECISION NOT NULL,
                        speed DOUBLE PRECISION,
                        event_type TEXT NOT NULL
);

-- Таблица ObjectZones
CREATE TABLE objectzones (
                             object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
                             zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE CASCADE,
                             entered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                             exited_at TIMESTAMP,
                             PRIMARY KEY (object_id, zone_id)
);

-- Таблица Alerts
CREATE TABLE alerts (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                        alert_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Таблица Routes
CREATE TABLE routes (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
                        name TEXT,
                        description TEXT,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP,
                        status TEXT NOT NULL DEFAULT 'PLANNED',
                        points JSONB NOT NULL,
                        metadata JSONB
);

-- Таблица Telemetry
CREATE TABLE telemetry (
                           id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                           object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
                           timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                           battery_level NUMERIC,
                           temperature NUMERIC,
                           signal_strength DOUBLE PRECISION,
                           additional_metrics JSONB
);

-- Таблица UserObject
CREATE TABLE userobject (
                            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                            object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
                            access_level TEXT NOT NULL,
                            PRIMARY KEY (user_id, object_id)
);

-- Создаем индексы

-- Для таблицы Events
CREATE INDEX IF NOT EXISTS idx_event_sensor_timestamp ON events(sensor_id, timestamp);

-- Для таблицы Alerts
CREATE INDEX IF NOT EXISTS idx_alert_event_type ON alerts(event_id, alert_type);
CREATE INDEX IF NOT EXISTS idx_alert_severity ON alerts(severity, created_at);

-- Для таблицы Routes
CREATE INDEX IF NOT EXISTS idx_route_object_time ON routes(object_id, start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_route_status ON routes(status);

-- Для таблицы Telemetry
CREATE INDEX IF NOT EXISTS idx_telemetry_object_time ON telemetry(object_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_signal ON telemetry(signal_strength);