import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client, Client

_supabase_client: Client = None

def get_db_client() -> Client:
    """
    Returns an initialized Supabase Client.
    """
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL", "")
        # Remove surrounding quotes if they exist
        if url.startswith('"') and url.endswith('"'):
            url = url[1:-1]
            
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY", "")
        if key.startswith('"') and key.endswith('"'):
            key = key[1:-1]
            
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY/SUPABASE_KEY must be set in environment.")
            
        _supabase_client = create_client(url, key)
    return _supabase_client

