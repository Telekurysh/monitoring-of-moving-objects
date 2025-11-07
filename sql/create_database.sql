-- Создание базы данных
DROP DATABASE IF EXISTS sensor;
CREATE DATABASE sensor;

-- После подключения к базе данных sensor (например, через \c sensor) включите расширение PostGIS:
CREATE EXTENSION IF NOT EXISTS postgis;