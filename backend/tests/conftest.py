"""Every test gets a fresh app wired to in-memory fake repositories (no Supabase needed)."""

import pytest

from app import create_app
from tests.fakes import FakePoolRepository, FakeUserRepository


@pytest.fixture
def user_repo():
    return FakeUserRepository()


@pytest.fixture
def pool_repo():
    return FakePoolRepository()


@pytest.fixture
def client(user_repo, pool_repo):
    app = create_app(user_repo=user_repo, pool_repo=pool_repo)
    app.testing = True
    return app.test_client()
