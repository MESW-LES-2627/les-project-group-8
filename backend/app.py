"""Friendly Pools API: wires the modules together.

Each module (users, pools) has routes -> service -> repository. This file only
builds those objects and registers them on the Flask app.

Run locally with `flask run`; Gunicorn uses `app:create_app()`.
"""

from flask import Flask, jsonify

from pools.repository import SupabasePoolRepository
from pools.routes import create_pools_blueprint
from pools.service import PoolService
from shared.auth import TokenVerifier, create_login_guard
from shared.db import get_supabase_client
from shared.errors import register_error_handlers
from users.repository import SupabaseUserRepository
from users.routes import create_users_blueprint
from users.service import UserService


def create_app(user_repo=None, pool_repo=None, token_verifier=None) -> Flask:
    """Tests pass in fake repositories and a verifier trusting their own key;
    otherwise the real Supabase ones are used."""
    app = Flask(__name__)

    if user_repo is None or pool_repo is None:
        db = get_supabase_client()
        user_repo = user_repo or SupabaseUserRepository(db)
        pool_repo = pool_repo or SupabasePoolRepository(db)
    token_verifier = token_verifier or TokenVerifier.from_env()

    user_service = UserService(user_repo)
    pool_service = PoolService(pool_repo, users=user_service)
    login_required = create_login_guard(token_verifier, user_service.get_user)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    app.register_blueprint(create_users_blueprint(user_service, login_required), url_prefix="/api")
    app.register_blueprint(create_pools_blueprint(pool_service), url_prefix="/api")
    register_error_handlers(app)
    return app
