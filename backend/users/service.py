"""Business rules for users."""

import uuid

from shared.errors import NotFoundError
from shared.validation import require_json_object, required_text

from .models import User

MAX_NAME_LENGTH = 80


class UserService:
    def __init__(self, repository):
        self._repository = repository

    def create_user(self, payload) -> User:
        payload = require_json_object(payload)
        user = User(id=str(uuid.uuid4()), name=required_text(payload, "name", MAX_NAME_LENGTH))
        self._repository.add(user)
        return user

    def get_user(self, user_id) -> User:
        user = self._repository.get(user_id) if _is_uuid(user_id) else None
        if user is None:
            raise NotFoundError("User not found.")
        return user


def _is_uuid(value) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False
