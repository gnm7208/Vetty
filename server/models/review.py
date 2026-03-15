"""Review domain model."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Text

from ..extensions import db
from .base import BaseModel, TimestampMixin


class Review(TimestampMixin, BaseModel):
    __tablename__ = "reviews"

    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    product_id = Column(ForeignKey("products.id"), nullable=True)
    service_id = Column(ForeignKey("services.id"), nullable=True)

    user = db.relationship("User", back_populates="reviews")
    product = db.relationship("Product", back_populates="reviews")
    service = db.relationship("Service", back_populates="reviews")

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_range"),
        CheckConstraint(
            "(product_id IS NOT NULL AND service_id IS NULL) OR (product_id IS NULL AND service_id IS NOT NULL)",
            name="ck_reviews_single_subject",
        ),
    )
