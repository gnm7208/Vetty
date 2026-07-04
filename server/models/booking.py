"""Service booking domain model."""

from __future__ import annotations

from sqlalchemy import Column, Enum, ForeignKey, Text
from sqlalchemy.types import DateTime

from ..extensions import db
from .base import BaseModel, TimestampMixin

BOOKING_STATUSES = (
    "pending",
    "approved",
    "declined",
    "completed",
    "cancelled",
)


class ServiceBooking(TimestampMixin, BaseModel):
    __tablename__ = "service_bookings"

    appointment_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(*BOOKING_STATUSES, name="booking_status"), nullable=False, default="pending")
    pet_details = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    service_id = Column(ForeignKey("services.id"), nullable=False)

    user = db.relationship("User", back_populates="bookings")
    service = db.relationship("Service", back_populates="bookings")
