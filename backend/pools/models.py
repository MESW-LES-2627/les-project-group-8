"""Plain data for the pools module."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from users.models import User


class PoolStatus(str, Enum):
    OPEN = "OPEN"
    LOCKED = "LOCKED"
    RESOLVED = "RESOLVED"


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
    statement: str
    deadline: datetime
    options: tuple[str, ...]
    creator: UserSummary
    decider: UserSummary


@dataclass(frozen=True)
class Pool:
    id: str
    name: str
    statement: str
    deadline: datetime
    creator: UserSummary
    decider: UserSummary
    options: tuple[Outcome, ...]
    winning_outcome_id: str | None
    created_at: datetime

    def status(self, now: datetime | None = None) -> PoolStatus:
        if self.winning_outcome_id is not None:
            return PoolStatus.RESOLVED
        now = now or datetime.now(timezone.utc)
        return PoolStatus.OPEN if now < self.deadline else PoolStatus.LOCKED
