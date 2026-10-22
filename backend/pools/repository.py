"""Database access for pools, using supabase-py. Rows are mapped to dataclasses by hand."""

from datetime import datetime

from .models import NewPool, Outcome, Pool, UserSummary

_POOL_COLUMNS = (
    "id, name, statement, deadline, winning_outcome_id, created_at,"
    " creator:users!creator_id(id, name),"
    " decider:users!decider_id(id, name),"
    " outcomes(id, label)"
)


class SupabasePoolRepository:
    def __init__(self, client):
        self._db = client

    def list_pools(self) -> list[Pool]:
        rows = self._db.table("pools").select(_POOL_COLUMNS).order("created_at", desc=True).execute().data
        return [_to_pool(row) for row in rows]

    def create_pool(self, new_pool: NewPool) -> Pool:
        pool_id = self._db.table("pools").insert({
            "name": new_pool.name,
            "statement": new_pool.statement,
            "deadline": new_pool.deadline.isoformat(),
            "creator_id": new_pool.creator.id,
            "decider_id": new_pool.decider.id,
        }).execute().data[0]["id"]

        # supabase-py cannot wrap both inserts in one transaction, so undo the pool by hand.
        try:
            self._db.table("outcomes").insert(
                [{"pool_id": pool_id, "label": label} for label in new_pool.options]
            ).execute()
        except Exception:
            self._db.table("pools").delete().eq("id", pool_id).execute()
            raise

        row = self._db.table("pools").select(_POOL_COLUMNS).eq("id", pool_id).single().execute().data
        return _to_pool(row)


def _to_pool(row: dict) -> Pool:
    return Pool(
        id=str(row["id"]),
        name=row["name"],
        statement=row["statement"],
        deadline=datetime.fromisoformat(row["deadline"]),
        creator=UserSummary(id=str(row["creator"]["id"]), name=row["creator"]["name"]),
        decider=UserSummary(id=str(row["decider"]["id"]), name=row["decider"]["name"]),
        options=tuple(Outcome(id=str(o["id"]), label=o["label"]) for o in row.get("outcomes") or []),
        winning_outcome_id=row.get("winning_outcome_id"),
        created_at=datetime.fromisoformat(row["created_at"]),
    )
