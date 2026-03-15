"""User domain model."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, Enum, String, Text
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from .base import BaseModel, TimestampMixin


USER_ROLES = ("customer", "admin")


class User(TimestampMixin, BaseModel):
    __tablename__ = "users"

    role = Column(Enum(*USER_ROLES, name="user_role"), nullable=False, default="customer")
    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(32), nullable=True)
    default_address = Column(Text, nullable=True)
    is_active = Column(db.Boolean, nullable=False, default=True)

    products = db.relationship(
        "Product",
        back_populates="creator",
        foreign_keys="Product.created_by_id",
        cascade="all, delete-orphan",
    )
    services = db.relationship(
        "Service",
        back_populates="creator",
        foreign_keys="Service.created_by_id",
        cascade="all, delete-orphan",
    )
    orders = db.relationship(
        "ProductOrder",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    bookings = db.relationship(
        "ServiceBooking",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reviews = db.relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    inventory_movements = db.relationship(
        "InventoryMovement",
        back_populates="actor",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("email <> ''", name="ck_users_email_nonempty"),
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)
