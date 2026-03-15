"""Product schemas."""

from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, validates


def _validate_sku(value: str) -> None:
    if len(value) < 3:
        raise ValidationError("SKU must be at least 3 characters long")


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    price_cents = fields.Int(required=True)
    stock_level = fields.Int(required=True)
    low_stock_threshold = fields.Int(required=True)
    sku = fields.Str(required=True)
    image_url = fields.Url(allow_none=True, schemes={"http", "https"})
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProductWriteSchema(Schema):
    name = fields.Str(required=True, validate=lambda s: 1 <= len(s) <= 160)
    description = fields.Str(allow_none=True)
    price_cents = fields.Int(required=True)
    stock_level = fields.Int(required=True)
    low_stock_threshold = fields.Int(required=True)
    sku = fields.Str(required=True, validate=_validate_sku)
    image_url = fields.Url(allow_none=True, schemes={"http", "https"})
    is_active = fields.Bool(load_default=True)

    @validates("price_cents")
    def validate_price(self, value: int) -> None:
        if value < 0:
            raise ValidationError("Price must be non-negative")

    @validates("stock_level")
    def validate_stock_level(self, value: int) -> None:
        if value < 0:
            raise ValidationError("Stock level must be non-negative")

    @validates("low_stock_threshold")
    def validate_low_stock(self, value: int) -> None:
        if value < 0:
            raise ValidationError("Low stock threshold must be non-negative")
