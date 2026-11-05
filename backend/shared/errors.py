"""Errors raised by services, and how they are turned into JSON responses."""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


class ValidationError(Exception):
    """The request breaks a business rule. Returned as 400."""


class NotFoundError(Exception):
    """The requested resource does not exist. Returned as 404."""


class AuthenticationError(Exception):
    """No valid access token: the caller is not logged in. Returned as 401."""


class ForbiddenError(Exception):
    """The caller is logged in but may not do this. Returned as 403."""


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def validation_error(err):
        return jsonify(error=str(err)), 400

    @app.errorhandler(AuthenticationError)
    def authentication_error(_err):
        return jsonify(error="Authentication required."), 401

    @app.errorhandler(ForbiddenError)
    def forbidden_error(err):
        return jsonify(error=str(err)), 403

    @app.errorhandler(NotFoundError)
    def not_found_error(err):
        return jsonify(error=str(err)), 404

    @app.errorhandler(HTTPException)
    def http_error(err):
        return jsonify(error=err.name), err.code

    @app.errorhandler(Exception)
    def unexpected_error(err):
        app.logger.exception("Unhandled error")
        return jsonify(error="Internal server error."), 500
