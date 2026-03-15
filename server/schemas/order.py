"""Order schemas."""

from __future__ import annotations

from marshmallow import Schema, ValidationError, fields, post_load, validates


class OrderItemSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    unit_price_cents = fields.Int(required=True)
    line_total_cents = fields.Int(required=True)

    @validates("quantity")
    def validate_quantity(self, value: int) -> None:
        if value <= 0:
            raise ValidationError("Quantity must be positive")

    @validates("unit_price_cents")
    def validate_unit_price(self, value: int) -> None:
        if value < 0:
            raise ValidationError("Unit price must be non-negative")

    @validates("line_total_cents")
    def validate_line_total(self, value: int) -> None:
        if value < 0:
            raise ValidationError("Line total must be non-negative")


class ProductOrderSchema(Schema):
    id = fields.Int(dump_only=True)
    order_number = fields.Str()
    status = fields.Str()
    subtotal_cents = fields.Int()
    tax_cents = fields.Int()
    delivery_fee_cents = fields.Int()
    total_cents = fields.Int()
    delivery_address = fields.Str()
    payment_reference = fields.Str(allow_none=True)
    items = fields.List(fields.Nested(OrderItemSchema))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ProductOrderWriteSchema(Schema):
    delivery_address = fields.Str(required=True)
    payment_reference = fields.Str(required=True)
    tax_cents = fields.Int(load_default=0)
    delivery_fee_cents = fields.Int(load_default=0)
    items = fields.List(fields.Nested(OrderItemSchema), required=True)

    @validates("payment_reference")
    def validate_payment_reference(self, value: str) -> None:
        if len(value) < 10 or len(value) > 12:
            raise ValidationError("Payment reference must be 10-12 characters long")

    @post_load
    def calculate_totals(self, data: dict, **_: dict) -> dict:
        subtotal = sum(item["line_total_cents"] for item in data["items"])
        data["subtotal_cents"] = subtotal
        data["total_cents"] = subtotal + data.get("tax_cents", 0) + data.get("delivery_fee_cents", 0)
        return data
