"""Read the User profiles created by Supabase Auth's signup trigger."""

from .models import User


class PsycopgUserRepository:
    def __init__(self, connect):
        self._connect = connect

    def get(self, user_id: str) -> User | None:
        with self._connect() as conn:
            row = conn.execute("SELECT id, name FROM users WHERE id = %s", (user_id,)).fetchone()
            return User(id=str(row["id"]), name=row["name"]) if row else None
