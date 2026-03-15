"""Shared utilities for REST resources."""

from __future__ import annotations

from http import HTTPStatus

from flask_jwt_extended import get_jwt, get_jwt_identity
from flask_restful import abort

from ..models import User


def get_current_user() -> User | None:
    identity = get_jwt_identity()
    if identity is None:
        return None
    return User.query.filter_by(id=identity, is_active=True).first()


def require_admin(user: User | None) -> None:
    if user is None or user.role != "admin":
        abort(HTTPStatus.FORBIDDEN, message="Admin privileges required")


def get_role() -> str | None:
    claims = get_jwt()
    return claims.get("role") if claims else None
