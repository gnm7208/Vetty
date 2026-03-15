"""Service catalog domain model."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Text

from ..extensions import db
from .base import BaseModel, TimestampMixin


class Service(TimestampMixin, BaseModel):
    __tablename__ = "services"

    title = Column(String(160), nullable=False)
    description = Column(Text, nullable=True)
    base_price_cents = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=30)
    is_active = Column(db.Boolean, nullable=False, default=True)
    created_by_id = Column(ForeignKey("users.id"), nullable=False)

    creator = db.relationship("User", back_populates="services")
    bookings = db.relationship(
        "ServiceBooking",
        back_populates="service",
        cascade="all, delete-orphan",
    )
    reviews = db.relationship(
        "Review",
        back_populates="service",
        cascade="all, delete-orphan",
    )
