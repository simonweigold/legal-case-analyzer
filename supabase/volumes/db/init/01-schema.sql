-- Legal Case Analyzer - Supabase Database Schema
-- This script sets up the database schema for self-hosted Supabase

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the application schema
CREATE SCHEMA IF NOT EXISTS legal_analyzer;

-- Grant permissions on application schema
GRANT ALL PRIVILEGES ON SCHEMA legal_analyzer TO supabase_auth_admin;
GRANT ALL PRIVILEGES ON SCHEMA legal_analyzer TO supabase_api_admin;
GRANT USAGE ON SCHEMA legal_analyzer TO supabase_realtime_admin;

-- Profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS legal_analyzer.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table
CREATE TABLE IF NOT EXISTS legal_analyzer.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES legal_analyzer.profiles(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) CHECK (category IN ('contract', 'litigation', 'compliance', 'research', 'other')) DEFAULT 'other',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    archived BOOLEAN DEFAULT FALSE
);

-- Messages table
CREATE TABLE IF NOT EXISTS legal_analyzer.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES legal_analyzer.conversations(id) ON DELETE CASCADE NOT NULL,
    role VARCHAR(20) CHECK (role IN ('user', 'assistant', 'system')) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON legal_analyzer.conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON legal_analyzer.conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_category ON legal_analyzer.conversations(category);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON legal_analyzer.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON legal_analyzer.messages(created_at);

-- Row Level Security (RLS) policies
ALTER TABLE legal_analyzer.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_analyzer.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_analyzer.messages ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON legal_analyzer.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON legal_analyzer.profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON legal_analyzer.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Conversations policies
CREATE POLICY "Users can view own conversations" ON legal_analyzer.conversations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own conversations" ON legal_analyzer.conversations
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own conversations" ON legal_analyzer.conversations
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own conversations" ON legal_analyzer.conversations
    FOR DELETE USING (auth.uid() = user_id);

-- Messages policies
CREATE POLICY "Users can view messages from own conversations" ON legal_analyzer.messages
    FOR SELECT USING (
        conversation_id IN (
            SELECT id FROM legal_analyzer.conversations WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages to own conversations" ON legal_analyzer.messages
    FOR INSERT WITH CHECK (
        conversation_id IN (
            SELECT id FROM legal_analyzer.conversations WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update messages from own conversations" ON legal_analyzer.messages
    FOR UPDATE USING (
        conversation_id IN (
            SELECT id FROM legal_analyzer.conversations WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete messages from own conversations" ON legal_analyzer.messages
    FOR DELETE USING (
        conversation_id IN (
            SELECT id FROM legal_analyzer.conversations WHERE user_id = auth.uid()
        )
    );

-- Function to handle user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO legal_analyzer.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create profile when user signs up
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON legal_analyzer.profiles
    FOR EACH ROW EXECUTE PROCEDURE public.update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON legal_analyzer.conversations
    FOR EACH ROW EXECUTE PROCEDURE public.update_updated_at_column();

-- Grant permissions to authenticated users
GRANT USAGE ON SCHEMA legal_analyzer TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA legal_analyzer TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA legal_analyzer TO authenticated;

-- Grant permissions to anon users (for public access if needed)
GRANT USAGE ON SCHEMA legal_analyzer TO anon;

-- Grant table permissions to Supabase users
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA legal_analyzer TO supabase_auth_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA legal_analyzer TO supabase_api_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA legal_analyzer TO supabase_realtime_admin;

-- Grant sequence permissions
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA legal_analyzer TO supabase_auth_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA legal_analyzer TO supabase_api_admin;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA legal_analyzer GRANT ALL PRIVILEGES ON TABLES TO supabase_auth_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA legal_analyzer GRANT ALL PRIVILEGES ON TABLES TO supabase_api_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA legal_analyzer GRANT SELECT ON TABLES TO supabase_realtime_admin;

-- Sample data for testing (optional)
-- Uncomment the following lines if you want sample data

-- INSERT INTO auth.users (id, email) VALUES 
--     ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com');

-- INSERT INTO legal_analyzer.profiles (id, email, full_name) VALUES 
--     ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com', 'Test User');

-- INSERT INTO legal_analyzer.conversations (id, user_id, title, category) VALUES 
--     ('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'Sample Legal Analysis', 'contract');

-- INSERT INTO legal_analyzer.messages (conversation_id, role, content) VALUES 
--     ('550e8400-e29b-41d4-a716-446655440001', 'user', 'Please analyze this employment contract.'),
--     ('550e8400-e29b-41d4-a716-446655440001', 'assistant', 'I''d be happy to help analyze the employment contract. Please provide the contract text or specific sections you''d like me to review.');
