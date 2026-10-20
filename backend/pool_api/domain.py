"""Compatibility helpers for domain types."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from app import GUEST_USER_ID, compute_status, validate_pool_payload

ValidationError = ValueError


class PoolStatus(str, Enum):
    OPEN = "OPEN"
    LOCKED = "LOCKED"
    RESOLVED = "RESOLVED"


class UserSummary:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Outcome:
    def __init__(self, id: str, label: str):
        self.id = id
        self.label = label

    def to_dict(self):
        return {"id": self.id, "label": self.label}


class Pool:
    def __init__(
        self,
        id: str,
        name: str,
        statement: str,
        deadline: datetime,
        creator: UserSummary,
        decider: UserSummary,
        options: tuple[Outcome, ...],
        winning_outcome_id: str | None = None,
    ):
        self.id = id
        self.name = name
        self.statement = statement
        self.deadline = deadline
        self.creator = creator
        self.decider = decider
        self.options = options
        self.winning_outcome_id = winning_outcome_id

    def status(self, now: datetime | None = None) -> PoolStatus:
        dl_str = self.deadline.isoformat() if hasattr(self.deadline, "isoformat") else str(self.deadline)
        return PoolStatus(compute_status(dl_str, self.winning_outcome_id, now=now))

    def to_dict(self) -> dict:
        dl_str = self.deadline.isoformat().replace("+00:00", "Z") if hasattr(self.deadline, "isoformat") else str(self.deadline)
        return {
            "id": self.id,
            "name": self.name,
            "statement": self.statement,
            "deadline": dl_str,
            "status": self.status().value,
            "winning_outcome_id": self.winning_outcome_id,
            "creator": self.creator.to_dict() if hasattr(self.creator, "to_dict") else self.creator,
            "decider": self.decider.to_dict() if hasattr(self.decider, "to_dict") else self.decider,
            "options": [o.to_dict() if hasattr(o, "to_dict") else o for o in self.options],
        }


class NewPool:
    def __init__(
        self,
        name: str,
        statement: str,
        deadline: datetime,
        options: tuple[str, ...],
        creator_id: str,
        decider_id: str | None = None,
    ):
        self.name = name
        self.statement = statement
        self.deadline = deadline
        self.options = tuple(options)
        self.creator_id = creator_id
        self.decider_id = decider_id or creator_id

    @classmethod
    def from_payload(cls, payload: dict, creator_id: str = GUEST_USER_ID, now: datetime | None = None) -> NewPool:
        validated = validate_pool_payload(payload, now=now)
        dl = datetime.fromisoformat(validated["deadline"].replace("Z", "+00:00"))
        return cls(
            name=validated["name"],
            statement=validated["statement"],
            deadline=dl,
            options=tuple(validated["options"]),
            creator_id=creator_id,
            decider_id=creator_id,
        )
