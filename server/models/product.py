"""Product catalog domain model."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text

from ..extensions import db
from .base import BaseModel, TimestampMixin


class Product(TimestampMixin, BaseModel):
    __tablename__ = "products"

    name = Column(String(160), nullable=False)
    description = Column(Text, nullable=True)
    price_cents = Column(Integer, nullable=False)
    stock_level = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=5)
    sku = Column(String(64), nullable=False, unique=True, index=True)
    image_url = Column(String(255), nullable=True)
    is_active = Column(db.Boolean, nullable=False, default=True)
    created_by_id = Column(ForeignKey("users.id"), nullable=False)

    creator = db.relationship("User", back_populates="products")
    order_items = db.relationship(
        "OrderItem",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    reviews = db.relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    inventory_movements = db.relationship(
        "InventoryMovement",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    def adjust_stock(self, delta: int) -> None:
        self.stock_level = (self.stock_level or 0) + delta
