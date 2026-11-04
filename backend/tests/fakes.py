"""In-memory test doubles for the repositories. Used only by tests, never by the app."""

import uuid
from dataclasses import replace
from datetime import datetime, timezone

from picks.models import Pick
from pools.models import NewPool, Outcome, Pool
from users.models import User


class FakeUserRepository:
    def __init__(self):
        self.users: dict[str, User] = {}

    def add(self, user: User) -> None:
        """Seeds a User, standing in for the sign-up trigger (the real repository has no `add`)."""
        self.users[user.id] = user

    def get(self, user_id: str) -> User | None:
        return self.users.get(user_id)


class FakePoolRepository:
    def __init__(self):
        self.pools: list[Pool] = []

    def list_pools(self) -> list[Pool]:
        return list(reversed(self.pools))

    def get_pool(self, pool_id: str) -> Pool | None:
        return next((pool for pool in self.pools if pool.id == pool_id), None)

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
            presentation=new_pool.presentation,
        )
        self.pools.append(pool)
        return pool


class FakePickRepository:
    def __init__(self):
        self.picks: dict[tuple[str, str], Pick] = {}

    def get(self, pool_id: str, user_id: str) -> Pick | None:
        return self.picks.get((pool_id, user_id))

    def create_or_replace(self, pool_id: str, user_id: str, outcome_id: str) -> Pick:
        key = (pool_id, user_id)
        existing = self.picks.get(key)
        pick = (
            replace(existing, outcome_id=outcome_id)
            if existing
            else Pick(
                id=str(uuid.uuid4()),
                pool_id=pool_id,
                user_id=user_id,
                outcome_id=outcome_id,
                created_at=datetime.now(timezone.utc),
            )
        )
        self.picks[key] = pick
        return pick
