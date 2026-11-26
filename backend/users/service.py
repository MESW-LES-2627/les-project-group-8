"""Business rules for users."""

import uuid

from shared.errors import NotFoundError, ValidationError
from shared.validation import require_json_object, required_text

from .models import User

MAX_NAME_LENGTH = 80


class UserService:
    def __init__(self, repository):
        self._repository = repository

    def get_user(self, user_id) -> User:
        user = self._repository.get(user_id) if _is_uuid(user_id) else None
        if user is None:
            raise NotFoundError("User not found.")
        return user

    def rename_user(self, user_id, payload) -> User:
        """Renames only the logged-in User; an id in the body would be another User's."""
        payload = require_json_object(payload)
        for field in ("id", "user_id"):
            if field in payload:
                raise ValidationError(
                    f"Field '{field}' is not accepted: you can only rename yourself."
                )
        name = required_text(payload, "name", MAX_NAME_LENGTH)
        user = self._repository.update_name(str(user_id), name)
        if user is None:
            raise NotFoundError("User not found.")
        return user


def _is_uuid(value) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False
