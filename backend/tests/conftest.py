import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app import GUEST_USER, GUEST_USER_ID, InMemoryStore, create_app


class InMemoryPoolRepository(InMemoryStore):
    """Test double so API tests run without Supabase."""
    pass


@pytest.fixture
def repo():
    return InMemoryPoolRepository()


@pytest.fixture
def client(repo):
    app = create_app(store=repo)
    app.testing = True
    return app.test_client()


@pytest.fixture
def valid_payload():
    deadline = datetime.now(timezone.utc) + timedelta(days=7)
    return {
        "name": "Champions League Final",
        "statement": "Real Madrid wins in 90 minutes.",
        "deadline": deadline.isoformat().replace("+00:00", "Z"),
        "options": ["Yes, they win", "No, draw or loss"],
    }
