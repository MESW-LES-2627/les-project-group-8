"""Public HTTP endpoint for pool leaderboards."""

from flask import Blueprint, jsonify

from .service import ScoreService


def create_scores_blueprint(service: ScoreService) -> Blueprint:
    blueprint = Blueprint("scores", __name__)

    @blueprint.get("/pools/<pool_id>/leaderboard")
    def get_leaderboard(pool_id):
        return jsonify([
            {
                "user": {"id": entry.user_id, "name": entry.user_name},
                "wins": entry.wins,
                "losses": entry.losses,
                "rank": entry.rank,
            }
            for entry in service.get_leaderboard(pool_id)
        ])

    return blueprint
