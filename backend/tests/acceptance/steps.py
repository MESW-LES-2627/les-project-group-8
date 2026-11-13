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


def sign_in(
    user_repo,
    name="Ana",
) -> tuple[User, dict]:
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


def create_pool(
    client,
    headers: dict,
    **overrides,
) -> dict:
    """Create a pool as the User the headers belong to."""
    response = client.post(
        "/api/pools",
        json=pool_payload(**overrides),
        headers=headers,
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def pool_payload(**overrides) -> dict:
    payload = {
        "name": "Champions League Final",
        "description": "Predictions for the final.",
        "deadline": iso(datetime.now(timezone.utc) + timedelta(days=7)),
    }
    payload.update(overrides)
    return payload


def create_bet(
    client,
    pool_id: str,
    headers: dict,
    **overrides,
) -> dict:
    """Add a Bet to an existing Pool as its creator."""
    response = client.post(
        f"/api/pools/{pool_id}/bets",
        json=bet_payload(**overrides),
        headers=headers,
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def bet_payload(**overrides) -> dict:
    payload = {
        "statement": "Real Madrid wins in 90 minutes.",
        "options": ["Yes, they win", "No, draw or loss"],
    }
    payload.update(overrides)
    return payload


def pick_payload(outcome_id: str) -> dict:
    return {"outcome_id": outcome_id}


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def seed_pick(client, pool_repo, pick_repo, user, pool, headers, *, winner=None, choice=0) -> dict:
    """Add a Bet as the Pool's creator, store the User's Pick on it, and resolve it if `winner` is set."""
    bet = create_bet(client, pool["id"], headers)
    pick_repo.create_or_replace(bet["id"], user.id, bet["options"][choice]["id"])
    if winner is not None:
        pool_repo.resolve_bet(pool["id"], bet["id"], bet["options"][winner]["id"])
    return bet


def leaderboard(client, pool) -> list:
    # Public: deliberately no Authorization header.
    response = client.get(f"/api/pools/{pool['id']}/leaderboard")
    assert response.status_code == 200
    return response.get_json()


def record(user, wins, losses, rank=1) -> dict:
    return {"user": {"id": user.id, "name": user.name}, "wins": wins, "losses": losses, "rank": rank}
