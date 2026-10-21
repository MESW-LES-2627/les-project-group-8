"""Pool creation rules and state, independent of Flask and persistence."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

GUEST_USER_ID = "00000000-0000-0000-0000-000000000001"

_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)
_OPTIONS_ERROR = "A pool must have exactly 2 unique, non-empty outcomes."


class ValidationError(ValueError):
    """Input does not satisfy the pool creation contract."""


def utc_timestamp(value: datetime) -> str:
    """Serialize an aware datetime as an explicit UTC timestamp."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone.")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_deadline(value: object) -> datetime:
    if not isinstance(value, str) or not _TIMESTAMP.fullmatch(value):
        raise ValidationError(
            "Field 'deadline' must be an ISO-8601 timestamp with a timezone."
        )
    try:
        return datetime.fromisoformat(value.upper().replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError as error:
        raise ValidationError("Field 'deadline' is not a valid ISO-8601 timestamp.") from error


def _required_text(payload: dict, field: str, max_length: int) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Field '{field}' cannot be empty.")
    if len(value) > max_length:
        raise ValidationError(f"Field '{field}' must be at most {max_length} characters.")
    return value.strip()


class PoolStatus(str, Enum):
    OPEN = "OPEN"
    LOCKED = "LOCKED"
    RESOLVED = "RESOLVED"


def _pool_status(
    deadline: datetime,
    winning_outcome_id: str | None,
    now: datetime | None,
) -> PoolStatus:
    if winning_outcome_id is not None:
        return PoolStatus.RESOLVED
    return PoolStatus.OPEN if deadline > (now or datetime.now(timezone.utc)) else PoolStatus.LOCKED


def compute_status(
    deadline_str: str,
    winning_outcome_id: str | None = None,
    now: datetime | None = None,
) -> str:
    return _pool_status(_parse_deadline(deadline_str), winning_outcome_id, now).value


@dataclass(frozen=True)
class UserSummary:
    id: str
    name: str

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}


@dataclass(frozen=True)
class Outcome:
    id: str
    label: str

    def to_dict(self) -> dict:
        return {"id": self.id, "label": self.label}


@dataclass(frozen=True)
class Pool:
    id: str
    name: str
    statement: str
    deadline: datetime
    creator: UserSummary
    decider: UserSummary
    options: tuple[Outcome, ...]
    winning_outcome_id: str | None = None

    def status(self, now: datetime | None = None) -> PoolStatus:
        return _pool_status(self.deadline, self.winning_outcome_id, now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "statement": self.statement,
            "deadline": utc_timestamp(self.deadline),
            "status": self.status().value,
            "winning_outcome_id": self.winning_outcome_id,
            "creator": self.creator.to_dict(),
            "decider": self.decider.to_dict(),
            "options": [option.to_dict() for option in self.options],
        }


@dataclass(frozen=True)
class NewPool:
    """Validated creation input; use from_payload at the application boundary."""

    name: str
    statement: str
    deadline: datetime
    options: tuple[str, ...]
    creator_id: str
    decider_id: str

    @classmethod
    def from_payload(
        cls,
        payload: object,
        creator_id: str = GUEST_USER_ID,
        now: datetime | None = None,
    ) -> NewPool:
        if not isinstance(payload, dict):
            raise ValidationError("Request body must be a JSON object.")

        name = _required_text(payload, "name", 120)
        statement = _required_text(payload, "statement", 500)
        options = payload.get("options")
        if not isinstance(options, list) or len(options) != 2:
            raise ValidationError(_OPTIONS_ERROR)

        cleaned_options = []
        seen = set()
        for option in options:
            if not isinstance(option, str) or not option.strip():
                raise ValidationError(_OPTIONS_ERROR)
            label = option.strip()
            if len(option) > 100:
                raise ValidationError("Each outcome label must be at most 100 characters.")
            if label.casefold() in seen:
                raise ValidationError(_OPTIONS_ERROR)
            seen.add(label.casefold())
            cleaned_options.append(label)

        deadline = _parse_deadline(payload.get("deadline"))
        if deadline <= (now or datetime.now(timezone.utc)):
            raise ValidationError("Field 'deadline' must be in the future.")

        return cls(
            name=name,
            statement=statement,
            deadline=deadline,
            options=tuple(cleaned_options),
            creator_id=creator_id,
            decider_id=creator_id,
        )

    def to_payload(self) -> dict:
        """Bridge to the existing stores while persistence is refactored separately."""
        return {
            "name": self.name,
            "statement": self.statement,
            "deadline": utc_timestamp(self.deadline),
            "options": list(self.options),
        }
