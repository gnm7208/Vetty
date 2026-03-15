"""Service booking schemas."""

from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, validates


class ServiceBookingSchema(Schema):
    id = fields.Int(dump_only=True)
    appointment_at = fields.DateTime(required=True)
    status = fields.Str()
    pet_details = fields.Str()
    address = fields.Str()
    notes = fields.Str(allow_none=True)
    service_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ServiceBookingWriteSchema(Schema):
    appointment_at = fields.DateTime(required=True)
    pet_details = fields.Str(required=True)
    address = fields.Str(required=True)
    notes = fields.Str(allow_none=True)
    service_id = fields.Int(required=True)

    @validates("pet_details")
    def validate_pet_details(self, value: str) -> None:
        if len(value) < 3:
            raise ValidationError("Pet details must have at least 3 characters")

    @validates("address")
    def validate_address(self, value: str) -> None:
        if len(value) < 5:
            raise ValidationError("Address must have at least 5 characters")
