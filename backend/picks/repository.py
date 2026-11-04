"""Database access for picks, using supabase-py. Rows are mapped to dataclasses by hand."""

from datetime import datetime

from .models import Pick

_PICK_COLUMNS = "id, pool_id, user_id, outcome_id, created_at"


class SupabasePickRepository:
    def __init__(self, client):
        self._db = client

    def get(self, pool_id: str, user_id: str) -> Pick | None:
        rows = (
            self._db.table("picks")
            .select(_PICK_COLUMNS)
            .eq("pool_id", pool_id)
            .eq("user_id", user_id)
            .execute()
            .data
        )
        return _to_pick(rows[0]) if rows else None

    def create_or_replace(self, pool_id: str, user_id: str, outcome_id: str) -> Pick:
        row = (
            self._db.table("picks")
            .upsert(
                {"pool_id": pool_id, "user_id": user_id, "outcome_id": outcome_id},
                on_conflict="pool_id,user_id",
            )
            .execute()
            .data[0]
        )
        return _to_pick(row)


def _to_pick(row: dict) -> Pick:
    return Pick(
        id=str(row["id"]),
        pool_id=str(row["pool_id"]),
        user_id=str(row["user_id"]),
        outcome_id=str(row["outcome_id"]),
        created_at=datetime.fromisoformat(row["created_at"]),
    )
