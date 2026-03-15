"""User-related Marshmallow schemas."""

from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, validates


def _validate_phone(value: str) -> None:
    if value and len(value) > 32:
        raise ValidationError("Phone number is too long")


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    role = fields.Str(dump_only=True)
    name = fields.Str()
    email = fields.Email()
    phone = fields.Str(validate=_validate_phone, allow_none=True)
    default_address = fields.Str(allow_none=True)
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserRegistrationSchema(Schema):
    name = fields.Str(required=True, validate=lambda s: 1 <= len(s) <= 120)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    phone = fields.Str(validate=_validate_phone, allow_none=True)
    default_address = fields.Str(allow_none=True)

    @validates("password")
    def validate_password_strength(self, value: str) -> None:
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long")


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class PasswordChangeSchema(Schema):
    current_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(required=True, load_only=True)

    @validates("new_password")
    def validate_new_password_strength(self, value: str) -> None:
        if len(value) < 8:
            raise ValidationError("New password must be at least 8 characters long")
