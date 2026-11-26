"""HTTP layer for users: who the logged-in User is, and what they are called.

Users are never created here: a database trigger creates each one when its Account signs up.
"""

from flask import Blueprint, jsonify, request

from shared.auth import LoginGuard

from .models import User
from .service import UserService


def create_users_blueprint(service: UserService, login_required: LoginGuard) -> Blueprint:
    blueprint = Blueprint("users", __name__)

    @blueprint.get("/me")
    @login_required
    def me(current_user: User):
        return jsonify(user_to_json(current_user))

    @blueprint.patch("/me")
    @login_required
    def rename_me(current_user: User):
        user = service.rename_user(current_user.id, request.get_json(silent=True))
        return jsonify(user_to_json(user))

    return blueprint


def user_to_json(user: User) -> dict:
    return {"id": user.id, "name": user.name}
