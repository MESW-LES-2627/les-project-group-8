"""HTTP layer for pools: parse the request, call the service, return JSON."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from shared.auth import LoginGuard
from users.models import User

from .models import Bet, Pool, UserSummary
from .service import PoolService


def create_pools_blueprint(service: PoolService, login_required: LoginGuard) -> Blueprint:
    blueprint = Blueprint("pools", __name__)

    @blueprint.get("/pools")
    def list_pools():
        return jsonify([pool_to_json(pool) for pool in service.list_pools()])

    @blueprint.get("/pools/<pool_id>")
    def get_pool(pool_id):
        return jsonify(pool_to_json(service.get_pool(pool_id)))

    @blueprint.post("/pools")
    @login_required
    def create_pool(current_user: User):
        pool = service.create_pool(request.get_json(silent=True), creator=current_user)
        return jsonify(pool_to_json(pool)), 201

    @blueprint.post("/pools/<pool_id>/bets")
    @login_required
    def create_bet(pool_id, current_user: User):
        bet = service.create_bet(pool_id, request.get_json(silent=True), creator=current_user)
        return jsonify(bet_to_json(bet)), 201

    return blueprint


def pool_to_json(pool: Pool) -> dict:
    return {
        "id": pool.id,
        "name": pool.name,
        "description": pool.description,
        "deadline": _utc_iso(pool.deadline),
        "status": pool.status().value,
        "creator": _user_to_json(pool.creator),
        "decider": _user_to_json(pool.decider),
        "bets": [bet_to_json(bet) for bet in pool.bets],
        "created_at": _utc_iso(pool.created_at),
    }


def bet_to_json(bet: Bet) -> dict:
    return {
        "id": bet.id,
        "pool_id": bet.pool_id,
        "statement": bet.statement,
        "presentation": bet.presentation.value,
        "winning_outcome_id": bet.winning_outcome_id,
        "options": [{"id": option.id, "label": option.label} for option in bet.options],
        "created_at": _utc_iso(bet.created_at),
    }


def _user_to_json(user: UserSummary) -> dict:
    return {"id": user.id, "name": user.name}


def _utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
