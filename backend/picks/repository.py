"""Database access for picks, using supabase-py. Rows are mapped to dataclasses by hand."""

from datetime import datetime

from .models import Pick

_PICK_COLUMNS = "id, bet_id, user_id, outcome_id, created_at"


class SupabasePickRepository:
    def __init__(self, client):
        self._db = client

    def list_user_picks(self, bet_ids: tuple[str, ...], user_id: str) -> list[Pick]:
        rows = (
            self._db.table("picks")
            .select(_PICK_COLUMNS)
            .in_("bet_id", list(bet_ids))
            .eq("user_id", user_id)
            .execute()
            .data
        )
        return [_to_pick(row) for row in rows]

    def create_or_replace(self, bet_id: str, user_id: str, outcome_id: str) -> Pick:
        row = (
            self._db.table("picks")
            .upsert(
                {"bet_id": bet_id, "user_id": user_id, "outcome_id": outcome_id},
                on_conflict="bet_id,user_id",
            )
            .execute()
            .data[0]
        )
        return _to_pick(row)


def _to_pick(row: dict) -> Pick:
    return Pick(
        id=str(row["id"]),
        bet_id=str(row["bet_id"]),
        user_id=str(row["user_id"]),
        outcome_id=str(row["outcome_id"]),
        created_at=datetime.fromisoformat(row["created_at"]),
    )
