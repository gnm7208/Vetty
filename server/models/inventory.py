"""Inventory tracking domain model."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.types import Text

from ..extensions import db
from .base import BaseModel, TimestampMixin


class InventoryMovement(TimestampMixin, BaseModel):
    __tablename__ = "inventory_movements"

    delta = Column(Integer, nullable=False)
    reason = Column(String(120), nullable=False)
    reference_type = Column(String(64), nullable=True)
    reference_id = Column(Integer, nullable=True)
    product_id = Column(ForeignKey("products.id"), nullable=False)
    actor_id = Column(ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)

    product = db.relationship("Product", back_populates="inventory_movements")
    actor = db.relationship("User", back_populates="inventory_movements")

    __table_args__ = (
        db.CheckConstraint("delta <> 0", name="ck_inventory_movement_nonzero"),
    )
