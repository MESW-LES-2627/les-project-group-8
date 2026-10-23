"""Supabase client used by every repository."""

import os

from dotenv import load_dotenv
from supabase import Client, create_client


def get_supabase_client() -> Client:
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set (see backend/.env.example).")
    return create_client(url, key)
