"""Inventory movement schemas."""

from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, validates


class InventoryMovementSchema(Schema):
    id = fields.Int(dump_only=True)
    delta = fields.Int(required=True)
    reason = fields.Str(required=True)
    reference_type = fields.Str(allow_none=True)
    reference_id = fields.Int(allow_none=True)
    notes = fields.Str(allow_none=True)
    product_id = fields.Int(required=True)
    actor_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class InventoryMovementWriteSchema(Schema):
    delta = fields.Int(required=True)
    reason = fields.Str(required=True, validate=lambda s: 1 <= len(s) <= 120)
    reference_type = fields.Str(allow_none=True)
    reference_id = fields.Int(allow_none=True)
    notes = fields.Str(allow_none=True)
    product_id = fields.Int(required=True)

    @validates("delta")
    def validate_delta(self, value: int) -> None:
        if value == 0:
            raise ValidationError("Delta cannot be zero")
