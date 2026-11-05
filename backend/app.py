"""Friendly Pools API: wires the modules together.

Each module (users, pools, picks) has routes -> service -> repository. This file
only builds those objects and registers them on the Flask app.

Run locally with `flask run`; Gunicorn uses `app:create_app()`.
"""

from flask import Flask, jsonify

from picks.repository import PsycopgPickRepository
from picks.routes import create_picks_blueprint
from picks.service import PickService
from pools.repository import PsycopgPoolRepository
from pools.routes import create_pools_blueprint
from pools.service import PoolService
from shared.auth import TokenVerifier, create_login_guard
from shared.db import get_connection_factory
from shared.errors import register_error_handlers
from users.repository import PsycopgUserRepository
from users.routes import create_users_blueprint
from users.service import UserService


def create_app(user_repo=None, pool_repo=None, pick_repo=None, token_verifier=None) -> Flask:
    """Tests pass in fake repositories and a verifier trusting their own key;
    otherwise use Psycopg repositories and Supabase Auth."""
    app = Flask(__name__)

    if user_repo is None or pool_repo is None or pick_repo is None:
        connect = get_connection_factory()
        user_repo = user_repo if user_repo is not None else PsycopgUserRepository(connect)
        pool_repo = pool_repo if pool_repo is not None else PsycopgPoolRepository(connect)
        pick_repo = pick_repo if pick_repo is not None else PsycopgPickRepository(connect)
    token_verifier = token_verifier or TokenVerifier.from_env()

    user_service = UserService(user_repo)
    pool_service = PoolService(pool_repo)
    pick_service = PickService(pick_repo, pools=pool_service)
    login_required = create_login_guard(token_verifier, user_service.get_user)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    app.register_blueprint(create_users_blueprint(login_required), url_prefix="/api")
    app.register_blueprint(create_pools_blueprint(pool_service, login_required), url_prefix="/api")
    app.register_blueprint(create_picks_blueprint(pick_service, login_required), url_prefix="/api")
    register_error_handlers(app)
    return app
