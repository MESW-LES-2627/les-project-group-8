"""Business rules for users."""

import uuid

from shared.errors import NotFoundError

from .models import User


class UserService:
    def __init__(self, repository):
        self._repository = repository

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
