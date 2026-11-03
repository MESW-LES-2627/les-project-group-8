"""HTTP layer for users: who the logged-in User is.

Users are never created here: a database trigger creates each one when its Account signs up.
"""

from flask import Blueprint, jsonify

from shared.auth import LoginGuard

from .models import User


def create_users_blueprint(login_required: LoginGuard) -> Blueprint:
    blueprint = Blueprint("users", __name__)

    @blueprint.get("/me")
    @login_required
    def me(current_user: User):
        return jsonify(user_to_json(current_user))

    return blueprint


def user_to_json(user: User) -> dict:
    return {"id": user.id, "name": user.name}
