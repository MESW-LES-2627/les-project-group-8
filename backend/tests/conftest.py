from datetime import datetime, timedelta, timezone

import pytest

from app import create_app
from tests.fakes import FakePoolRepository, FakeUserRepository


@pytest.fixture
def user_repo():
    return FakeUserRepository()


@pytest.fixture
def repo():
    return FakePoolRepository()


@pytest.fixture
def client(user_repo, repo):
    app = create_app(user_repo=user_repo, pool_repo=repo)
    app.testing = True
    return app.test_client()


@pytest.fixture
def creator(client):
    return client.post("/api/users", json={"name": "Ana"}).get_json()


@pytest.fixture
def valid_payload(creator):
    deadline = datetime.now(timezone.utc) + timedelta(days=7)
    return {
        "creator_id": creator["id"],
        "name": "Champions League Final",
        "statement": "Real Madrid wins in 90 minutes.",
        "deadline": deadline.isoformat().replace("+00:00", "Z"),
        "options": ["Yes, they win", "No, draw or loss"],
    }
