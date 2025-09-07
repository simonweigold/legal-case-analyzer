-- Supabase Auth Database Initialization
-- This script sets up the required auth schema and users for self-hosted Supabase

-- Create the auth schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS auth;

-- Create auth users table if it doesn't exist
CREATE TABLE IF NOT EXISTS auth.users (
    instance_id UUID,
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    aud VARCHAR(255),
    role VARCHAR(255),
    email VARCHAR(255),
    encrypted_password VARCHAR(255),
    email_confirmed_at TIMESTAMP WITH TIME ZONE,
    invited_at TIMESTAMP WITH TIME ZONE,
    confirmation_token VARCHAR(255),
    confirmation_sent_at TIMESTAMP WITH TIME ZONE,
    recovery_token VARCHAR(255),
    recovery_sent_at TIMESTAMP WITH TIME ZONE,
    email_change_token_new VARCHAR(255),
    email_change VARCHAR(255),
    email_change_sent_at TIMESTAMP WITH TIME ZONE,
    last_sign_in_at TIMESTAMP WITH TIME ZONE,
    raw_app_meta_data JSONB,
    raw_user_meta_data JSONB,
    is_super_admin BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    phone TEXT DEFAULT NULL,
    phone_confirmed_at TIMESTAMP WITH TIME ZONE,
    phone_change TEXT DEFAULT NULL,
    phone_change_token VARCHAR(255) DEFAULT NULL,
    phone_change_sent_at TIMESTAMP WITH TIME ZONE,
    confirmed_at TIMESTAMP WITH TIME ZONE GENERATED ALWAYS AS (LEAST(email_confirmed_at, phone_confirmed_at)) STORED,
    email_change_token_current VARCHAR(255) DEFAULT NULL,
    email_change_confirm_status SMALLINT DEFAULT 0,
    banned_until TIMESTAMP WITH TIME ZONE,
    reauthentication_token VARCHAR(255) DEFAULT NULL,
    reauthentication_sent_at TIMESTAMP WITH TIME ZONE,
    is_sso_user BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes on auth.users
CREATE UNIQUE INDEX IF NOT EXISTS users_email_idx ON auth.users (email);
CREATE INDEX IF NOT EXISTS users_instance_id_idx ON auth.users (instance_id);

-- Create the auth.uid() function
CREATE OR REPLACE FUNCTION auth.uid() RETURNS UUID
    LANGUAGE sql STABLE
    AS $$
  SELECT 
    COALESCE(
        nullif(current_setting('request.jwt.claim.sub', true), ''),
        (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub')
    )::uuid
$$;

-- Create the auth.role() function
CREATE OR REPLACE FUNCTION auth.role() RETURNS TEXT
    LANGUAGE sql STABLE
    AS $$
  SELECT 
    COALESCE(
        nullif(current_setting('request.jwt.claim.role', true), ''),
        (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role')
    )::text
$$;

-- Create auth schema users with appropriate permissions
DO $$
BEGIN
    -- Create supabase_auth_admin user
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'supabase_auth_admin') THEN
        CREATE USER supabase_auth_admin WITH PASSWORD '${POSTGRES_PASSWORD}' CREATEDB;
    END IF;
    
    -- Create supabase_api_admin user  
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'supabase_api_admin') THEN
        CREATE USER supabase_api_admin WITH PASSWORD '${POSTGRES_PASSWORD}';
    END IF;
    
    -- Create supabase_realtime_admin user
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'supabase_realtime_admin') THEN
        CREATE USER supabase_realtime_admin WITH PASSWORD '${POSTGRES_PASSWORD}';
    END IF;
END $$;

-- Grant permissions to auth admin
GRANT ALL PRIVILEGES ON SCHEMA auth TO supabase_auth_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth TO supabase_auth_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA auth TO supabase_auth_admin;

-- Grant permissions to api admin
GRANT USAGE ON SCHEMA auth TO supabase_api_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA auth TO supabase_api_admin;

-- Grant permissions to realtime admin  
GRANT USAGE ON SCHEMA auth TO supabase_realtime_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA auth TO supabase_realtime_admin;

-- Grant permissions on public schema
GRANT ALL PRIVILEGES ON SCHEMA public TO supabase_auth_admin;
GRANT ALL PRIVILEGES ON SCHEMA public TO supabase_api_admin;
GRANT USAGE ON SCHEMA public TO supabase_realtime_admin;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT ALL PRIVILEGES ON TABLES TO supabase_auth_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO supabase_api_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT SELECT ON TABLES TO supabase_realtime_admin;
