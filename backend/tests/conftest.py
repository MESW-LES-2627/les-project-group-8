from datetime import datetime, timedelta, timezone

import pytest

from app import create_app
from tests.fakes import FakePoolRepository


@pytest.fixture
def repo():
    return FakePoolRepository()


@pytest.fixture
def client(repo):
    app = create_app(pool_repo=repo)
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
