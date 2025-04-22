from supabase import create_client, Client
import os
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_by_github_id(github_id: str) -> dict:
    response = supabase.table("users").select("*").eq("github_id", github_id).execute()
    return response.data[0] if response.data else None


