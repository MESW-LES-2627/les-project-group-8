"""HTTP layer for users: parse the request, call the service, return JSON."""

from flask import Blueprint, jsonify, request

from .models import User
from .service import UserService


def create_users_blueprint(service: UserService, login_required) -> Blueprint:
    blueprint = Blueprint("users", __name__)

    @blueprint.post("/users")
    def create_user():
        user = service.create_user(request.get_json(silent=True))
        return jsonify(user_to_json(user)), 201

    @blueprint.get("/me")
    @login_required
    def me(current_user: User):
        return jsonify(user_to_json(current_user))

    return blueprint


def user_to_json(user: User) -> dict:
    return {"id": user.id, "name": user.name}
