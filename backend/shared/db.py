"""PostgreSQL connections; Supabase Auth uses its own configuration."""

import os
from functools import partial
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


def get_connection_factory():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL must be set (see backend/.env.example).")
    # Compatible with Supabase's transaction pooler as well as direct connections.
    return partial(psycopg.connect, url, row_factory=dict_row,
                   connect_timeout=10, prepare_threshold=None)
