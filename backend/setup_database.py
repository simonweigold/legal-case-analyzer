#!/usr/bin/env python3
"""
Script to initialize Supabase database tables for the Legal Case Analyzer.
Run this script to set up the required tables in your Supabase PostgreSQL database.
"""

import os
import sys
from supabase_config import get_supabase_service
from database_schema import INITIAL_SETUP_QUERIES

def setup_database():
    """Set up the database tables and policies."""
    try:
        print("🔄 Setting up Supabase database...")
        
        # Get service role client for admin operations
        supabase = get_supabase_service()
        
        # Execute each setup query
        for i, query in enumerate(INITIAL_SETUP_QUERIES, 1):
            print(f"📝 Executing query {i}/{len(INITIAL_SETUP_QUERIES)}...")
            try:
                result = supabase.rpc('exec_sql', {'query': query}).execute()
                print(f"✅ Query {i} executed successfully")
            except Exception as e:
                print(f"⚠️  Query {i} failed (this might be expected if tables already exist): {str(e)}")
        
        print("\n🎉 Database setup completed!")
        print("\n📋 Next steps:")
        print("1. Update your .env file with your actual Supabase keys")
        print("2. Make sure your Supabase instance is running")
        print("3. Start the backend: python3 main.py")
        print("4. Start the frontend: cd ../frontend && bun dev")
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure your Supabase instance is running")
        print("2. Check your .env file has the correct SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        print("3. Verify your service role key has admin privileges")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()
