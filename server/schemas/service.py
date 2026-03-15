"""Service schemas."""

from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, validates


class ServiceSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    base_price_cents = fields.Int(required=True)
    duration_minutes = fields.Int(required=True)
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ServiceWriteSchema(Schema):
    title = fields.Str(required=True, validate=lambda s: 1 <= len(s) <= 160)
    description = fields.Str(allow_none=True)
    base_price_cents = fields.Int(required=True)
    duration_minutes = fields.Int(required=True)
    is_active = fields.Bool(load_default=True)

    @validates("base_price_cents")
    def validate_price(self, value: int) -> None:
        if value < 0:
            raise ValidationError("Base price must be non-negative")

    @validates("duration_minutes")
    def validate_duration(self, value: int) -> None:
        if value <= 0:
            raise ValidationError("Duration must be positive")
