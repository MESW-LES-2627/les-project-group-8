"""In-memory test doubles for the repositories. Used only by tests, never by the app."""

import uuid
from dataclasses import replace
from datetime import datetime, timezone

from picks.models import Pick
from pools.models import Bet, NewBet, NewPool, Outcome, Pool
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

    def create_pool(
        self,
        new_pool: NewPool,
    ) -> Pool:
        pool = Pool(
            id=str(uuid.uuid4()),
            name=new_pool.name,
            description=new_pool.description,
            deadline=new_pool.deadline,
            creator=new_pool.creator,
            decider=new_pool.decider,
            created_at=datetime.now(timezone.utc),
        )
        self.pools.append(pool)
        return pool

    def create_bet(
        self,
        pool_id: str,
        new_bet: NewBet,
    ) -> Bet:
        bet = Bet(
            id=str(uuid.uuid4()),
            pool_id=pool_id,
            statement=new_bet.statement,
            options=tuple(
                Outcome(id=str(uuid.uuid4()), label=label)
                for label in new_bet.options
            ),
            winning_outcome_id=None,
            created_at=datetime.now(timezone.utc),
            presentation=new_bet.presentation,
        )
        for index, pool in enumerate(self.pools):
            if pool.id == pool_id:
                self.pools[index] = replace(pool, bets=pool.bets + (bet,))
                return bet
        raise AssertionError("Cannot seed a bet without its pool.")

    def resolve_bet(self, pool_id: str, bet_id: str, winning_outcome_id: str) -> Bet | None:
        for index, pool in enumerate(self.pools):
            if pool.id == pool_id:
                bet = pool.find_bet(bet_id)
                if bet is None:
                    return None
                resolved = replace(bet, winning_outcome_id=winning_outcome_id)
                self.pools[index] = replace(
                    pool, bets=tuple(resolved if item.id == bet_id else item for item in pool.bets),
                )
                return resolved
        return None


class FakePickRepository:
    def __init__(self, users: FakeUserRepository):
        self._users = users
        self.picks: dict[tuple[str, str], Pick] = {}

    def get(
        self,
        bet_id: str,
        user_id: str,
    ) -> Pick | None:
        return self.picks.get((bet_id, user_id))

    def list_user_picks(
        self,
        bet_ids: tuple[str, ...],
        user_id: str,
    ) -> list[Pick]:
        return [pick for pick in self.list_all_picks(bet_ids) if pick.user_id == user_id]

    def list_all_picks(
        self,
        bet_ids: tuple[str, ...],
    ) -> list[Pick]:
        return [
            replace(pick, user=self._users.get(pick.user_id))
            for pick in self.picks.values()
            if pick.bet_id in bet_ids
        ]

    def create_or_replace(
        self,
        bet_id: str,
        user_id: str,
        outcome_id: str,
    ) -> Pick:
        key = (bet_id, user_id)
        existing = self.picks.get(key)
        pick = (
            replace(existing, outcome_id=outcome_id)
            if existing
            else Pick(
                id=str(uuid.uuid4()),
                bet_id=bet_id,
                user_id=user_id,
                outcome_id=outcome_id,
                created_at=datetime.now(timezone.utc),
                user=self._users.get(user_id),
            )
        )
        self.picks[key] = pick
        return pick
