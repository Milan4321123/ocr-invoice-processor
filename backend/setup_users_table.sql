-- Users table for authentication
-- Run this SQL in your Supabase SQL editor to create the users table

CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on username for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Add RLS (Row Level Security) policy - for now allow all operations
-- You can make this more restrictive later
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy to allow all operations for authenticated users
CREATE POLICY "Allow all operations for authenticated users" ON users
    FOR ALL USING (true);

-- NOTE: Default admin user will be created automatically by the application
-- based on environment variables (ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL)
-- This provides better security than hardcoded credentials

-- Optional: Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE PROCEDURE update_updated_at_column();
