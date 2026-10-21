"""Friendly Pools API: wires the modules together.

Each module (pools, ...) has routes -> service -> repository. This file only
builds those objects and registers them on the Flask app.

Run locally with `flask run`; Gunicorn uses `app:create_app()`.
"""

from flask import Flask, jsonify

from pools.repository import SupabasePoolRepository
from pools.routes import create_pools_blueprint
from pools.service import PoolService
from shared.db import get_supabase_client
from shared.errors import register_error_handlers


def create_app(pool_repo=None) -> Flask:
    """Tests pass in a fake repository; otherwise the real Supabase one is used."""
    app = Flask(__name__)

    if pool_repo is None:
        pool_repo = SupabasePoolRepository(get_supabase_client())

    pool_service = PoolService(pool_repo)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    app.register_blueprint(create_pools_blueprint(pool_service), url_prefix="/api")
    register_error_handlers(app)
    return app
