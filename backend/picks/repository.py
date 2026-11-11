"""Database access for picks, using supabase-py. Rows are mapped to dataclasses by hand."""

from datetime import datetime

from users.models import User

from .models import Pick

_PICK_COLUMNS = "id, bet_id, user_id, outcome_id, created_at, user:users!user_id(id, name)"


class SupabasePickRepository:
    def __init__(self, client):
        self._db = client

    def list_user_picks(self, bet_ids: tuple[str, ...], user_id: str) -> list[Pick]:
        return _execute(self._picks_for(bet_ids).eq("user_id", user_id))

    def list_all_picks(self, bet_ids: tuple[str, ...]) -> list[Pick]:
        return _execute(self._picks_for(bet_ids))

    def _picks_for(self, bet_ids: tuple[str, ...]):
        return self._db.table("picks").select(_PICK_COLUMNS).in_("bet_id", list(bet_ids))

    def create_or_replace(self, bet_id: str, user_id: str, outcome_id: str) -> Pick:
        row = (
            self._db.table("picks")
            .upsert(
                {"bet_id": bet_id, "user_id": user_id, "outcome_id": outcome_id},
                on_conflict="bet_id,user_id",
            )
            .select(_PICK_COLUMNS)
            .execute()
            .data[0]
        )
        return _to_pick(row)


def _execute(query) -> list[Pick]:
    return [_to_pick(row) for row in query.order("created_at").order("id").execute().data]


def _to_pick(row: dict) -> Pick:
    return Pick(
        id=str(row["id"]),
        bet_id=str(row["bet_id"]),
        user_id=str(row["user_id"]),
        outcome_id=str(row["outcome_id"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        user=User(id=str(row["user"]["id"]), name=row["user"]["name"]),
    )
