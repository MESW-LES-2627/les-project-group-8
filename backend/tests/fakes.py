"""In-memory test doubles for the repositories. Used only by tests, never by the app."""

import uuid
from datetime import datetime, timezone

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
