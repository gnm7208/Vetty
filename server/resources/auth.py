"""Authentication resources."""

from __future__ import annotations

from http import HTTPStatus

from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_restful import Resource

from ..extensions import db
from ..models import User
from ..schemas import (
    PasswordChangeSchema,
    UserLoginSchema,
    UserRegistrationSchema,
    UserSchema,
)

user_schema = UserSchema()
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
password_change_schema = PasswordChangeSchema()


class RegisterResource(Resource):
    def post(self):
        payload = request.get_json() or {}
        data = user_registration_schema.load(payload)

        if User.query.filter_by(email=data["email"].lower()).first():
            return {"error": "Email already registered"}, HTTPStatus.CONFLICT

        user = User(
            name=data["name"],
            email=data["email"].lower(),
            phone=data.get("phone"),
            default_address=data.get("default_address"),
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        tokens = _issue_tokens(user)
        response = user_schema.dump(user)
        response.update(tokens)
        return response, HTTPStatus.CREATED


class LoginResource(Resource):
    def post(self):
        payload = request.get_json() or {}
        data = user_login_schema.load(payload)

        user = User.query.filter_by(email=data["email"].lower(), is_active=True).first()
        if not user or not user.check_password(data["password"]):
            return {"error": "Invalid credentials"}, HTTPStatus.UNAUTHORIZED

        tokens = _issue_tokens(user)
        response = user_schema.dump(user)
        response.update(tokens)
        return response, HTTPStatus.OK


class ProfileResource(Resource):
    @jwt_required()
    def get(self):
        current_user = _get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND
        return user_schema.dump(current_user), HTTPStatus.OK

    @jwt_required()
    def patch(self):
        current_user = _get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        payload = request.get_json() or {}
        updatable_fields = {"name", "phone", "default_address"}
        for field in updatable_fields:
            if field in payload:
                setattr(current_user, field, payload[field])

        db.session.commit()
        return user_schema.dump(current_user), HTTPStatus.OK


class PasswordChangeResource(Resource):
    @jwt_required()
    def post(self):
        current_user = _get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        payload = request.get_json() or {}
        data = password_change_schema.load(payload)

        if not current_user.check_password(data["current_password"]):
            return {"error": "Current password is incorrect"}, HTTPStatus.UNAUTHORIZED

        current_user.set_password(data["new_password"])
        db.session.commit()
        return {"message": "Password updated"}, HTTPStatus.OK


class TokenRefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = _get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        access_token = create_access_token(identity=current_user)
        return {"access_token": access_token}, HTTPStatus.OK


def _issue_tokens(user: User) -> dict[str, str]:
    access_token = create_access_token(identity=user, additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=user)
    return {"access_token": access_token, "refresh_token": refresh_token}


def _get_current_user() -> User | None:
    identity = get_jwt_identity()
    if identity is None:
        return None
    return User.query.filter_by(id=identity, is_active=True).first()
