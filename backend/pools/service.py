"""Business rules for pools."""

import uuid
from datetime import datetime, timezone

from shared.errors import NotFoundError, ValidationError
from shared.validation import require_json_object, required_text
from users.models import User

from .models import NewPool, Pool, PoolPresentation, UserSummary

MAX_NAME_LENGTH = 120
MAX_STATEMENT_LENGTH = 500
MIN_OPTIONS = 2
MAX_OPTIONS = 10
MAX_OPTION_LENGTH = 100


class PoolService:
    def __init__(self, repository):
        self._repository = repository

    def list_pools(self) -> list[Pool]:
        return self._repository.list_pools()

    def get_pool(self, pool_id) -> Pool:
        pool = self._repository.get_pool(str(pool_id)) if _is_uuid(pool_id) else None
        if pool is None:
            raise NotFoundError("Pool not found.")
        return pool

    def create_pool(self, payload, creator: User) -> Pool:
        """`creator` is the logged-in User; they also become the decider."""
        payload = require_json_object(payload)
        if "creator_id" in payload:
            # The old way of choosing who creates a pool; refused so clients notice it is gone.
            raise ValidationError("Field 'creator_id' is not accepted: the creator is the logged-in user.")
        new_pool = parse_new_pool(payload, creator=UserSummary.of(creator))
        return self._repository.create_pool(new_pool)


def parse_new_pool(payload, creator: UserSummary, now: datetime | None = None) -> NewPool:
    payload = require_json_object(payload)
    return NewPool(
        name=required_text(payload, "name", MAX_NAME_LENGTH),
        statement=required_text(payload, "statement", MAX_STATEMENT_LENGTH),
        deadline=_future_deadline(payload.get("deadline"), now or datetime.now(timezone.utc)),
        options=_options(payload.get("options")),
        presentation=_presentation(payload.get("presentation")),
        creator=creator,
        decider=creator,
    )


def _options(raw) -> tuple[str, ...]:
    error = ValidationError(
        f"A question must have between {MIN_OPTIONS} and {MAX_OPTIONS} unique, non-empty options."
    )
    if not isinstance(raw, list) or not MIN_OPTIONS <= len(raw) <= MAX_OPTIONS:
        raise error
    if not all(isinstance(option, str) and option.strip() for option in raw):
        raise error
    options = tuple(option.strip() for option in raw)
    if any(len(option) > MAX_OPTION_LENGTH for option in options):
        raise ValidationError(f"Each option must be at most {MAX_OPTION_LENGTH} characters.")
    if len({option.casefold() for option in options}) != len(options):
        raise error
    return options


def _presentation(raw) -> PoolPresentation:
    if raw is None:
        return PoolPresentation.RADIO
    if not isinstance(raw, str) or raw.lower() not in {item.value for item in PoolPresentation}:
        raise ValidationError("Field 'presentation' must be 'radio' or 'dropdown'.")
    return PoolPresentation(raw.lower())


def _future_deadline(raw, now: datetime) -> datetime:
    if not isinstance(raw, str):
        raise ValidationError("Field 'deadline' must be an ISO-8601 string.")
    try:
        deadline = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        raise ValidationError("Field 'deadline' is not a valid ISO-8601 timestamp.")
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if deadline <= now:
        raise ValidationError("Field 'deadline' must be in the future.")
    return deadline.astimezone(timezone.utc)


def _is_uuid(value) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False
