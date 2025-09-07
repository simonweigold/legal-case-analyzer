"""
Supabase configuration and client setup for the Legal Case Analyzer backend.
"""
import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "http://localhost:54321")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

class SupabaseClient:
    """Supabase client wrapper for database operations."""
    
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        # Create client with anon key for user operations
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Create service role client for admin operations
        if SUPABASE_SERVICE_ROLE_KEY:
            self.service_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        else:
            self.service_client = self.client

    def get_client(self, use_service_role: bool = False) -> Client:
        """Get the appropriate Supabase client."""
        return self.service_client if use_service_role else self.client

# Global Supabase client instance
supabase_client = SupabaseClient()

def get_supabase() -> Client:
    """Get the Supabase client instance."""
    return supabase_client.get_client()

def get_supabase_service() -> Client:
    """Get the Supabase service role client instance."""
    return supabase_client.get_client(use_service_role=True)
