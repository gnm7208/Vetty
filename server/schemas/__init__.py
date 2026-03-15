"""Marshmallow schemas for Vetty payload validation and serialization."""

from __future__ import annotations

from flask_marshmallow import Marshmallow

from .booking import ServiceBookingSchema, ServiceBookingWriteSchema
from .inventory import InventoryMovementSchema, InventoryMovementWriteSchema
from .order import OrderItemSchema, ProductOrderSchema, ProductOrderWriteSchema
from .product import ProductSchema, ProductWriteSchema
from .review import ReviewSchema, ReviewWriteSchema
from .service import ServiceSchema, ServiceWriteSchema
from .user import (
    PasswordChangeSchema,
    UserLoginSchema,
    UserRegistrationSchema,
    UserSchema,
)

ma = Marshmallow()


__all__ = [
    "ma",
    "UserSchema",
    "UserRegistrationSchema",
    "UserLoginSchema",
    "PasswordChangeSchema",
    "ProductSchema",
    "ProductWriteSchema",
    "ServiceSchema",
    "ServiceWriteSchema",
    "ProductOrderSchema",
    "ProductOrderWriteSchema",
    "OrderItemSchema",
    "ServiceBookingSchema",
    "ServiceBookingWriteSchema",
    "ReviewSchema",
    "ReviewWriteSchema",
    "InventoryMovementSchema",
    "InventoryMovementWriteSchema",
]
