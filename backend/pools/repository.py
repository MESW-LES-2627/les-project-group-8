"""Pool and Bet persistence with one transaction per write operation."""

from collections import defaultdict

from .models import Bet, BetPresentation, NewBet, NewPool, Outcome, Pool, UserSummary

_POOL_SELECT = """
    SELECT p.*, creator.name AS creator_name, decider.name AS decider_name
    FROM pools p JOIN users creator ON creator.id = p.creator_id
    JOIN users decider ON decider.id = p.decider_id
"""
_BET_SELECT = """
    SELECT b.*, COALESCE(
        json_agg(json_build_object('id', o.id, 'label', o.label) ORDER BY o.position)
        FILTER (WHERE o.id IS NOT NULL), '[]'::json
    ) AS options
    FROM bets b LEFT JOIN outcomes o ON o.bet_id = b.id
"""


class PsycopgPoolRepository:
    def __init__(self, connect):
        self._connect = connect

    def list_pools(self) -> list[Pool]:
        with self._connect() as conn:
            return _read_pools(conn)

    def get_pool(self, pool_id: str) -> Pool | None:
        with self._connect() as conn:
            pools = _read_pools(conn, pool_id)
            return pools[0] if pools else None

    def create_pool(self, new_pool: NewPool) -> Pool:
        # The context commits only after every insert and the response read
        # succeed; any exception rolls back and closes this connection.
        with self._connect() as conn:
            pool_id = conn.execute(
                """INSERT INTO pools (name, description, deadline, creator_id, decider_id)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (new_pool.name, new_pool.description, new_pool.deadline,
                 new_pool.creator.id, new_pool.decider.id),
            ).fetchone()["id"]
            conn.execute(
                "INSERT INTO rounds (pool_id, deadline) VALUES (%s, %s)",
                (pool_id, new_pool.deadline),
            )
            for bet in new_pool.initial_bets:
                _insert_bet(conn, pool_id, bet)
            return _read_pools(conn, pool_id)[0]

    def create_bet(self, pool_id: str, new_bet: NewBet) -> Bet:
        with self._connect() as conn:
            return _insert_bet(conn, pool_id, new_bet)


def _insert_bet(conn, pool_id, new_bet: NewBet) -> Bet:
    bet_id = conn.execute(
        """INSERT INTO bets (pool_id, round_id, statement, presentation, created_at)
           VALUES (%s, (SELECT id FROM rounds WHERE pool_id = %s), %s, %s, clock_timestamp())
           RETURNING id""",
        (pool_id, pool_id, new_bet.statement, new_bet.presentation.value),
    ).fetchone()["id"]
    with conn.cursor() as cursor:
        cursor.executemany(
            "INSERT INTO outcomes (bet_id, label, position) VALUES (%s, %s, %s)",
            [(bet_id, label, position) for position, label in enumerate(new_bet.options)],
        )
    row = conn.execute(_BET_SELECT + " WHERE b.id = %s GROUP BY b.id", (bet_id,)).fetchone()
    return _to_bet(row)


def _read_pools(conn, pool_id=None) -> list[Pool]:
    where, params = ("", ()) if pool_id is None else (" WHERE p.id = %s", (pool_id,))
    rows = conn.execute(_POOL_SELECT + where + " ORDER BY p.created_at DESC, p.id", params).fetchall()
    if not rows:
        return []
    bets = defaultdict(list)
    for row in conn.execute(
        _BET_SELECT + " WHERE b.pool_id = ANY(%s::uuid[]) GROUP BY b.id ORDER BY b.created_at, b.id",
        ([row["id"] for row in rows],),
    ).fetchall():
        bets[row["pool_id"]].append(_to_bet(row))
    return [Pool(
        id=str(row["id"]), name=row["name"], description=row["description"],
        deadline=row["deadline"], created_at=row["created_at"],
        creator=UserSummary(str(row["creator_id"]), row["creator_name"]),
        decider=UserSummary(str(row["decider_id"]), row["decider_name"]),
        bets=tuple(bets[row["id"]]),
    ) for row in rows]


def _to_bet(row) -> Bet:
    return Bet(
        id=str(row["id"]), pool_id=str(row["pool_id"]), statement=row["statement"],
        options=tuple(Outcome(str(o["id"]), o["label"]) for o in row["options"]),
        winning_outcome_id=str(row["winning_outcome_id"]) if row["winning_outcome_id"] else None,
        created_at=row["created_at"], presentation=BetPresentation(row["presentation"]),
    )
