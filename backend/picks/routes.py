"""HTTP layer for picks: parse the request, call the service, return JSON."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from shared.auth import LoginGuard
from users.models import User

from .models import Pick
from .service import PickService


def create_picks_blueprint(service: PickService, login_required: LoginGuard) -> Blueprint:
    blueprint = Blueprint("picks", __name__)

    @blueprint.get("/pools/<pool_id>/picks")
    @login_required
    def list_picks(pool_id, current_user: User):
        picks = service.list_picks(pool_id, current_user)
        return jsonify(picks=[pick_to_json(pick) for pick in picks])

    @blueprint.post("/pools/<pool_id>/bets/<bet_id>/picks")
    @login_required
    def save_pick(pool_id, bet_id, current_user: User):
        pick = service.save_pick(pool_id, bet_id, request.get_json(silent=True), current_user)
        return jsonify(pick_to_json(pick)), 201

    return blueprint


def pick_to_json(pick: Pick) -> dict:
    return {
        "id": pick.id,
        "bet_id": pick.bet_id,
        "user_id": pick.user_id,
        "user": {"id": pick.user.id, "name": pick.user.name},
        "outcome_id": pick.outcome_id,
        "created_at": _utc_iso(pick.created_at),
    }


def _utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
