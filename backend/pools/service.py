"""Business rules for pools."""

from datetime import datetime, timezone

from shared.errors import NotFoundError, ValidationError
from shared.validation import require_json_object, required_text
from users.service import UserService

from .models import NewPool, Pool, UserSummary

MAX_NAME_LENGTH = 120
MAX_STATEMENT_LENGTH = 500
OUTCOMES_PER_POOL = 2


class PoolService:
    def __init__(self, repository, users: UserService):
        self._repository = repository
        self._users = users

    def list_pools(self) -> list[Pool]:
        return self._repository.list_pools()

    def create_pool(self, payload) -> Pool:
        payload = require_json_object(payload)
        new_pool = parse_new_pool(payload, creator=self._find_creator(payload.get("creator_id")))
        return self._repository.create_pool(new_pool)

    def _find_creator(self, creator_id) -> UserSummary:
        try:
            user = self._users.get_user(creator_id)
        except NotFoundError:
            raise ValidationError("Field 'creator_id' must be the id of an existing user.")
        return UserSummary(id=user.id, name=user.name)


def parse_new_pool(payload, creator: UserSummary, now: datetime | None = None) -> NewPool:
    payload = require_json_object(payload)
    return NewPool(
        name=required_text(payload, "name", MAX_NAME_LENGTH),
        statement=required_text(payload, "statement", MAX_STATEMENT_LENGTH),
        deadline=_future_deadline(payload.get("deadline"), now or datetime.now(timezone.utc)),
        options=_options(payload.get("options")),
        creator=creator,
        decider=creator,
    )


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
