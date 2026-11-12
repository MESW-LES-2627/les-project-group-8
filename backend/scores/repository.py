"""Database read projection joining picks to their users and bets."""

from .models import ScoringPick

_COLUMNS = (
    "id, outcome_id, user:users!user_id(id, name),"
    " bet:bets!inner(pool_id, winning_outcome_id)"
)
_PAGE_SIZE = 1000


class SupabaseScoreRepository:
    def __init__(self, client):
        self._db = client

    def list_scoring_picks(self, pool_id: str) -> list[ScoringPick]:
        picks = []
        offset = 0
        while True:
            rows = (
                self._db.table("picks")
                .select(_COLUMNS)
                .eq("bet.pool_id", pool_id)
                .order("id")
                .range(offset, offset + _PAGE_SIZE - 1)
                .execute().data
            )
            picks.extend(
                ScoringPick(
                    user_id=str(row["user"]["id"]),
                    user_name=row["user"]["name"],
                    outcome_id=str(row["outcome_id"]),
                    winning_outcome_id=row["bet"]["winning_outcome_id"],
                )
                for row in rows
            )
            if len(rows) < _PAGE_SIZE:
                return picks
            offset += _PAGE_SIZE
