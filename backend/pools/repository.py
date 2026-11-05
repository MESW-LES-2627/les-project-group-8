"""Database access for pools, using supabase-py. Rows are mapped to dataclasses by hand."""

from datetime import datetime

from .models import Bet, BetPresentation, NewBet, NewPool, Outcome, Pool, UserSummary

_BET_COLUMNS = (
    "id, pool_id, statement, winning_outcome_id, created_at, presentation,"
    " outcomes!outcomes_bet_id_fkey(id, label, position)"
)

_POOL_COLUMNS = (
    "id, name, description, deadline, created_at,"
    " creator:users!creator_id(id, name),"
    " decider:users!decider_id(id, name),"
    f" bets({_BET_COLUMNS})"
)


class SupabasePoolRepository:
    def __init__(self, client):
        self._db = client

    def list_pools(self) -> list[Pool]:
        rows = (
            self._db.table("pools")
            .select(_POOL_COLUMNS)
            .order("created_at", desc=True)
            .execute()
            .data
        )
        return [_to_pool(row) for row in rows]

    def get_pool(self, pool_id: str) -> Pool | None:
        rows = self._db.table("pools").select(_POOL_COLUMNS).eq("id", pool_id).execute().data
        return _to_pool(rows[0]) if rows else None

    def create_pool(self, new_pool: NewPool) -> Pool:
        pool_id = self._db.table("pools").insert({
            "name": new_pool.name,
            "description": new_pool.description,
            "deadline": new_pool.deadline.isoformat(),
            "creator_id": new_pool.creator.id,
            "decider_id": new_pool.decider.id,
        }).execute().data[0]["id"]

        row = (
            self._db.table("pools")
            .select(_POOL_COLUMNS)
            .eq("id", pool_id)
            .single()
            .execute()
            .data
        )
        return _to_pool(row)

    def create_bet(self, pool_id: str, new_bet: NewBet) -> Bet:
        bet_id = self._db.table("bets").insert({
            "pool_id": pool_id,
            "statement": new_bet.statement,
            "presentation": new_bet.presentation.value,
        }).execute().data[0]["id"]

        # Keep the existing cleanup approach until #31 introduces transactions.
        try:
            self._db.table("outcomes").insert(
                [
                    {"bet_id": bet_id, "label": label, "position": position}
                    for position, label in enumerate(new_bet.options)
                ]
            ).execute()
        except Exception:
            self._db.table("bets").delete().eq("id", bet_id).execute()
            raise

        row = (
            self._db.table("bets")
            .select(_BET_COLUMNS)
            .eq("id", bet_id)
            .single()
            .execute()
            .data
        )
        return _to_bet(row)


def _to_pool(row: dict) -> Pool:
    bets = sorted(
        (_to_bet(bet) for bet in row.get("bets") or []),
        key=lambda bet: (bet.created_at, bet.id),
    )
    return Pool(
        id=str(row["id"]),
        name=row["name"],
        description=row["description"],
        deadline=datetime.fromisoformat(row["deadline"]),
        creator=UserSummary(id=str(row["creator"]["id"]), name=row["creator"]["name"]),
        decider=UserSummary(id=str(row["decider"]["id"]), name=row["decider"]["name"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        bets=tuple(bets),
    )


def _to_bet(row: dict) -> Bet:
    options = sorted(row.get("outcomes") or [], key=lambda outcome: outcome["position"])
    return Bet(
        id=str(row["id"]),
        pool_id=str(row["pool_id"]),
        statement=row["statement"],
        options=tuple(Outcome(id=str(option["id"]), label=option["label"]) for option in options),
        winning_outcome_id=row.get("winning_outcome_id"),
        created_at=datetime.fromisoformat(row["created_at"]),
        presentation=BetPresentation(row["presentation"]),
    )
