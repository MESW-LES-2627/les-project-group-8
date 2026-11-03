"""Who is calling: verifies Supabase access tokens and guards routes that need a logged-in User.

Tokens are checked locally against Supabase's public signing keys (ADR 0001).
"""

import os
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import request

from .errors import AuthenticationError, ForbiddenError, NotFoundError

ALGORITHM = "ES256"
AUDIENCE = "authenticated"


class TokenVerifier:
    """Checks a token's signature, expiry and audience, and returns its `sub`: the User's id."""

    def __init__(self, signing_key_for):
        self._signing_key_for = signing_key_for

    @classmethod
    def for_public_key(cls, public_key) -> "TokenVerifier":
        """Trusts one fixed key, e.g. a throwaway key pair in tests."""
        return cls(lambda _token: public_key)

    @classmethod
    def for_jwks(cls, jwks_url: str) -> "TokenVerifier":
        """Trusts the published key set. It is fetched once and cached; an unknown `kid` refetches it
        (at most once every 30 s, PyJWKClient's cooldown, so bogus `kid`s can't flood Supabase)."""
        client = jwt.PyJWKClient(jwks_url)
        return cls(lambda token: client.get_signing_key_from_jwt(token).key)

    @classmethod
    def from_env(cls) -> "TokenVerifier":
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        if not url:
            raise RuntimeError("SUPABASE_URL must be set (see backend/.env.example).")
        return cls.for_jwks(f"{url.rstrip('/')}/auth/v1/.well-known/jwks.json")

    def user_id(self, token: str) -> str:
        try:
            claims = jwt.decode(
                token,
                self._signing_key_for(token),
                algorithms=[ALGORITHM],
                audience=AUDIENCE,
                options={"require": ["exp", "aud", "sub"]},
            )
        except jwt.PyJWKClientConnectionError:
            raise  # Supabase unreachable: our failure, not the caller's, so not a 401.
        except jwt.PyJWTError as err:
            raise AuthenticationError() from err
        return claims["sub"]


def create_login_guard(verifier: TokenVerifier, load_user):
    """Builds `@login_required`: the route runs only for a logged-in User, passed in as `current_user`.

    `load_user(user_id)` returns the User or raises NotFoundError.
    """

    def login_required(route):
        @wraps(route)
        def guarded(*args, **kwargs):
            user_id = verifier.user_id(_bearer_token())
            try:
                user = load_user(user_id)
            except NotFoundError as err:
                raise ForbiddenError("No user exists for this account.") from err
            return route(*args, current_user=user, **kwargs)

        return guarded

    return login_required


def _bearer_token() -> str:
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise AuthenticationError()
    return token.strip()
