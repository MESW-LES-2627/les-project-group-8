"""In-memory test double for the pool repository. Used only by tests, never by the app."""

import uuid
from datetime import datetime, timezone

from pools.models import NewPool, Outcome, Pool


class FakePoolRepository:
    def __init__(self):
        self.pools: list[Pool] = []

    def list_pools(self) -> list[Pool]:
        return list(reversed(self.pools))

    def create_pool(self, new_pool: NewPool) -> Pool:
        pool = Pool(
            id=str(uuid.uuid4()),
            name=new_pool.name,
            statement=new_pool.statement,
            deadline=new_pool.deadline,
            creator=new_pool.creator,
            decider=new_pool.decider,
            options=tuple(Outcome(id=str(uuid.uuid4()), label=label) for label in new_pool.options),
            winning_outcome_id=None,
            created_at=datetime.now(timezone.utc),
        )
        self.pools.append(pool)
        return pool
