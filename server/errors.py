"""Application-wide error handling utilities."""

from __future__ import annotations

from flask import Flask, jsonify
from marshmallow import ValidationError


def register_error_handlers(app: Flask) -> None:
    """Attach shared error handlers to the Flask app."""

    @app.errorhandler(ValidationError)
    def handle_validation_error(exc: ValidationError):  # pragma: no cover simple
        return jsonify({"errors": exc.messages}), 422

    @app.errorhandler(404)
    def handle_not_found(_: Exception):  # pragma: no cover simple
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_server_error(exc: Exception):  # pragma: no cover simple
        app.logger.exception("Unhandled server error", exc_info=exc)
        return jsonify({"error": "Internal server error"}), 500
