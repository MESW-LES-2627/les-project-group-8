"""Every test gets a fresh app wired to in-memory fake repositories (no Supabase needed)
and a token verifier that trusts the test signing key."""

import pytest

from app import create_app
from shared.auth import TokenVerifier
from tests.acceptance.steps import SIGNING_KEY
from tests.fakes import FakePoolRepository, FakeUserRepository


@pytest.fixture
def user_repo():
    return FakeUserRepository()


@pytest.fixture
def pool_repo():
    return FakePoolRepository()


@pytest.fixture
def client(user_repo, pool_repo):
    app = create_app(
        user_repo=user_repo,
        pool_repo=pool_repo,
        token_verifier=TokenVerifier.for_public_key(SIGNING_KEY.public_key()),
    )
    app.testing = True
    return app.test_client()
