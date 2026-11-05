"""Plain data for the pools module."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from users.models import User


class PoolStatus(str, Enum):
    OPEN = "OPEN"
    LOCKED = "LOCKED"


class BetPresentation(str, Enum):
    """How a Bet renders its options."""

    RADIO = "radio"
    DROPDOWN = "dropdown"


@dataclass(frozen=True)
class UserSummary:
    """How a pool refers to a user: just enough to display them."""

    id: str
    name: str

    @classmethod
    def of(cls, user: User) -> "UserSummary":
        return cls(id=user.id, name=user.name)


@dataclass(frozen=True)
class Outcome:
    id: str
    label: str


@dataclass(frozen=True)
class NewPool:
    """A validated pool that has not been saved yet."""

    name: str
    description: str
    deadline: datetime
    creator: UserSummary
    decider: UserSummary
    initial_bets: tuple["NewBet", ...] = ()


@dataclass(frozen=True)
class NewBet:
    statement: str
    options: tuple[str, ...]
    presentation: BetPresentation = BetPresentation.RADIO


@dataclass(frozen=True)
class Bet:
    id: str
    pool_id: str
    statement: str
    options: tuple[Outcome, ...]
    winning_outcome_id: str | None
    created_at: datetime
    presentation: BetPresentation = BetPresentation.RADIO


@dataclass(frozen=True)
class Pool:
    id: str
    name: str
    description: str
    deadline: datetime
    creator: UserSummary
    decider: UserSummary
    created_at: datetime
    bets: tuple[Bet, ...] = ()

    def status(self, now: datetime | None = None) -> PoolStatus:
        now = now or datetime.now(timezone.utc)
        return PoolStatus.OPEN if now < self.deadline else PoolStatus.LOCKED

    def find_bet(self, bet_id: str) -> Bet | None:
        return next((bet for bet in self.bets if bet.id == bet_id), None)
