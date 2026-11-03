"""Database access for users, using supabase-py. Rows are mapped to dataclasses by hand."""

from .models import User


class SupabaseUserRepository:
    def __init__(self, client):
        self._db = client

    def get(self, user_id: str) -> User | None:
        rows = self._db.table("users").select("id, name").eq("id", user_id).limit(1).execute().data
        return User(id=str(rows[0]["id"]), name=rows[0]["name"]) if rows else None
