"""Authentication helpers and JWT configuration."""

from __future__ import annotations

from flask import jsonify
from flask_jwt_extended import JWTManager

from ..models import User


def register_jwt_callbacks(jwt: JWTManager) -> None:
    """Configure JWT callbacks for user loading and error handling."""

    @jwt.user_identity_loader
    def user_identity_lookup(user: User) -> int:  # pragma: no cover - simple wiring
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity, is_active=True).first()

    @jwt.invalid_token_loader
    def invalid_token_callback(reason: str):  # pragma: no cover - integration path
        return jsonify({"error": "Invalid token", "reason": reason}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(reason: str):  # pragma: no cover - integration path
        return jsonify({"error": "Authorization required", "reason": reason}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):  # pragma: no cover - integration path
        return jsonify({"error": "Token has expired"}), 401
