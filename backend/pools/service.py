"""Business rules for pools."""

from datetime import datetime, timezone

from shared.errors import ValidationError

from .models import NewPool, Pool, UserSummary

GUEST_USER = UserSummary(id="00000000-0000-0000-0000-000000000001", name="Guest User")

MAX_NAME_LENGTH = 120
MAX_STATEMENT_LENGTH = 500
OUTCOMES_PER_POOL = 2


class PoolService:
    def __init__(self, repository):
        self._repository = repository

    def list_pools(self) -> list[Pool]:
        return self._repository.list_pools()

    def create_pool(self, payload: dict) -> Pool:
        new_pool = parse_new_pool(payload, creator=GUEST_USER)
        return self._repository.create_pool(new_pool)


def parse_new_pool(payload, creator: UserSummary, now: datetime | None = None) -> NewPool:
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")
    return NewPool(
        name=_required_text(payload, "name", MAX_NAME_LENGTH),
        statement=_required_text(payload, "statement", MAX_STATEMENT_LENGTH),
        deadline=_future_deadline(payload.get("deadline"), now or datetime.now(timezone.utc)),
        options=_options(payload.get("options")),
        creator=creator,
        decider=creator,
    )


def _required_text(payload: dict, field: str, max_length: int) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Field '{field}' cannot be empty.")
    value = value.strip()
    if len(value) > max_length:
        raise ValidationError(f"Field '{field}' must be at most {max_length} characters.")
    return value


def _options(raw) -> tuple[str, ...]:
    error = ValidationError(f"A pool must have exactly {OUTCOMES_PER_POOL} unique, non-empty outcomes.")
    if not isinstance(raw, list) or len(raw) != OUTCOMES_PER_POOL:
        raise error
    if not all(isinstance(option, str) and option.strip() for option in raw):
        raise error
    options = tuple(option.strip() for option in raw)
    if len({option.casefold() for option in options}) != len(options):
        raise error
    return options


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
