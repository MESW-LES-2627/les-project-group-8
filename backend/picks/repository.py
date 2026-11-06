"""PostgreSQL persistence for per-User, per-Bet Picks."""

from .models import Pick


class PsycopgPickRepository:
    def __init__(self, connect):
        self._connect = connect

    def list_user_picks(self, bet_ids: tuple[str, ...], user_id: str) -> list[Pick]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM picks WHERE bet_id = ANY(%s::uuid[]) AND user_id = %s",
                (list(bet_ids), user_id),
            ).fetchall()
            return [_to_pick(row) for row in rows]

    def create_or_replace(self, bet_id: str, user_id: str, outcome_id: str) -> Pick:
        with self._connect() as conn:
            row = conn.execute(
                """INSERT INTO picks (bet_id, user_id, outcome_id) VALUES (%s, %s, %s)
                   ON CONFLICT (bet_id, user_id) DO UPDATE SET outcome_id = EXCLUDED.outcome_id
                   RETURNING *""",
                (bet_id, user_id, outcome_id),
            ).fetchone()
            return _to_pick(row)


def _to_pick(row) -> Pick:
    return Pick(id=str(row["id"]), bet_id=str(row["bet_id"]), user_id=str(row["user_id"]),
                outcome_id=str(row["outcome_id"]), created_at=row["created_at"])
