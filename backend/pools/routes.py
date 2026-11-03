"""HTTP layer for pools: parse the request, call the service, return JSON."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from shared.auth import LoginGuard
from users.models import User

from .models import Pool, UserSummary
from .service import PoolService


def create_pools_blueprint(service: PoolService, login_required: LoginGuard) -> Blueprint:
    blueprint = Blueprint("pools", __name__)

    @blueprint.get("/pools")
    def list_pools():
        return jsonify([pool_to_json(pool) for pool in service.list_pools()])

    @blueprint.post("/pools")
    @login_required
    def create_pool(current_user: User):
        pool = service.create_pool(request.get_json(silent=True), creator=current_user)
        return jsonify(pool_to_json(pool)), 201

    return blueprint


def pool_to_json(pool: Pool) -> dict:
    return {
        "id": pool.id,
        "name": pool.name,
        "statement": pool.statement,
        "deadline": _utc_iso(pool.deadline),
        "status": pool.status().value,
        "winning_outcome_id": pool.winning_outcome_id,
        "creator": _user_to_json(pool.creator),
        "decider": _user_to_json(pool.decider),
        "options": [{"id": o.id, "label": o.label} for o in pool.options],
        "created_at": _utc_iso(pool.created_at),
    }


def _user_to_json(user: UserSummary) -> dict:
    return {"id": user.id, "name": user.name}


def _utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
