-- Create read-only user for replica reads
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ro_user') THEN
      CREATE ROLE ro_user WITH LOGIN PASSWORD 'ro_password' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
   END IF;
END$$;

-- Grant SELECT on all existing tables in public schema
GRANT CONNECT ON DATABASE sensortrack TO ro_user;

\c sensortrack

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
        EXECUTE format('GRANT SELECT ON TABLE public.%I TO ro_user;', r.tablename);
    END LOOP;
END$$;
