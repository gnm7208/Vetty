"""Order domain models."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, Integer, String, Text

from ..extensions import db
from .base import BaseModel, TimestampMixin


ORDER_STATUSES = (
    "pending",
    "approved",
    "dispatched",
    "delivered",
    "cancelled",
)


class ProductOrder(TimestampMixin, BaseModel):
    __tablename__ = "product_orders"

    order_number = Column(String(32), nullable=False, unique=True, index=True)
    status = Column(Enum(*ORDER_STATUSES, name="order_status"), nullable=False, default="pending")
    subtotal_cents = Column(Integer, nullable=False, default=0)
    tax_cents = Column(Integer, nullable=False, default=0)
    delivery_fee_cents = Column(Integer, nullable=False, default=0)
    total_cents = Column(Integer, nullable=False, default=0)
    delivery_address = Column(Text, nullable=False)
    payment_reference = Column(String(64), nullable=True, index=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("subtotal_cents >= 0", name="ck_order_subtotal_nonnegative"),
        CheckConstraint("tax_cents >= 0", name="ck_order_tax_nonnegative"),
        CheckConstraint("delivery_fee_cents >= 0", name="ck_order_delivery_nonnegative"),
        CheckConstraint("total_cents >= 0", name="ck_order_total_nonnegative"),
    )


class OrderItem(TimestampMixin, BaseModel):
    __tablename__ = "order_items"

    quantity = Column(Integer, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    line_total_cents = Column(Integer, nullable=False)
    order_id = Column(ForeignKey("product_orders.id"), nullable=False)
    product_id = Column(ForeignKey("products.id"), nullable=False)

    order = db.relationship("ProductOrder", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_item_quantity_positive"),
        CheckConstraint("unit_price_cents >= 0", name="ck_order_item_unit_price_nonnegative"),
        CheckConstraint("line_total_cents >= 0", name="ck_order_item_line_total_nonnegative"),
    )
