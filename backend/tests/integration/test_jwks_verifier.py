"""The production TokenVerifier, built from the environment, against a local key-set server that counts fetches:
it builds one key-set client and caches Supabase's published keys (ADR 0001). The client's own refetch
and cooldown are PyJWT's behaviour, so they are not tested here."""

import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from jwt.algorithms import ECAlgorithm

import shared.auth
from shared.auth import TokenVerifier

JWKS_PATH = "/auth/v1/.well-known/jwks.json"
KEYS = {"old": ec.generate_private_key(ec.SECP256R1())}


class KeySetServer:
    """Serves the public halves of KEYS at JWKS_PATH and counts the requests."""

    def __init__(self):
        self.fetches = 0
        server = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                assert self.path == JWKS_PATH
                server.fetches += 1
                body = json.dumps({"keys": [_jwk(kid) for kid in KEYS]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self._httpd.server_port}"
        threading.Thread(target=self._httpd.serve_forever, daemon=True).start()

    def close(self):
        self._httpd.shutdown()
        self._httpd.server_close()


def _jwk(kid: str) -> dict:
    return {**ECAlgorithm.to_jwk(KEYS[kid].public_key(), as_dict=True), "kid": kid, "alg": "ES256", "use": "sig"}


def _token(kid: str) -> str:
    claims = {"sub": "ana", "aud": "authenticated", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    return jwt.encode(claims, KEYS[kid], algorithm="ES256", headers={"kid": kid})


@pytest.fixture
def key_set():
    server = KeySetServer()
    yield server
    server.close()


@pytest.fixture
def no_dotenv(monkeypatch):
    """A developer's backend/.env must not leak into these tests."""
    monkeypatch.setattr(shared.auth, "load_dotenv", lambda: None)


def test_key_set_is_fetched_once_for_many_tokens(key_set, no_dotenv, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", key_set.url + "/")
    verifier = TokenVerifier.from_env()

    for _ in range(3):
        assert verifier.user_id(_token("old")) == "ana"
    assert key_set.fetches == 1


def test_an_unreachable_key_set_is_not_blamed_on_the_caller(key_set, no_dotenv, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", key_set.url)
    verifier = TokenVerifier.from_env()
    key_set.close()

    with pytest.raises(jwt.PyJWKClientConnectionError):
        verifier.user_id(_token("old"))


def test_building_the_verifier_without_supabase_url_fails_clearly(no_dotenv, monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="SUPABASE_URL must be set"):
        TokenVerifier.from_env()
