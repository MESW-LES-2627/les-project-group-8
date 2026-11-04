"""Reusable "Given" steps, so each test reads like its acceptance criterion."""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from cryptography.hazmat.primitives.asymmetric import ec

from users.models import User

# Throwaway ES256 key pair: the app under test trusts SIGNING_KEY's public half,
# so tokens signed with it go through the real verification. FORGERY_KEY is not trusted.
SIGNING_KEY = ec.generate_private_key(ec.SECP256R1())
FORGERY_KEY = ec.generate_private_key(ec.SECP256R1())


def sign_in(user_repo, name="Ana") -> tuple[User, dict]:
    """Seed a User and return it with auth headers carrying a valid token for it."""
    user = User(id=str(uuid.uuid4()), name=name)
    user_repo.add(user)
    return user, bearer(token_for(user.id))


def token_for(
    user_id: str,
    *,
    expires_in: timedelta = timedelta(hours=1),
    audience: str = "authenticated",
    key=SIGNING_KEY,
) -> str:
    """A Supabase-style access token; override one part for an expired, wrong-audience or forged one."""
    claims = {"sub": user_id, "aud": audience, "exp": datetime.now(timezone.utc) + expires_in}
    return jwt.encode(claims, key, algorithm="ES256")


def expired_token(user_id: str) -> str:
    return token_for(user_id, expires_in=timedelta(minutes=-5))


def wrong_audience_token(user_id: str) -> str:
    return token_for(user_id, audience="anon")


def forged_token(user_id: str) -> str:
    return token_for(user_id, key=FORGERY_KEY)


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_pool(client, headers: dict, **overrides) -> dict:
    """Create a pool as the User the headers belong to."""
    response = client.post("/api/pools", json=pool_payload(**overrides), headers=headers)
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def pool_payload(**overrides) -> dict:
    payload = {
        "name": "Champions League Final",
        "statement": "Real Madrid wins in 90 minutes.",
        "deadline": iso(datetime.now(timezone.utc) + timedelta(days=7)),
        "options": ["Yes, they win", "No, draw or loss"],
    }
    payload.update(overrides)
    return payload


def pick_payload(outcome_id: str) -> dict:
    return {"outcome_id": outcome_id}


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
