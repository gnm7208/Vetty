"""Shared model mixins and base classes."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, func

from ..extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class HasStatusMixin:
    """Marker mixin to provide transition helpers."""

    status: str

    def transition_to(self, new_status: str) -> None:
        self.status = new_status
        if hasattr(self, "updated_at") and isinstance(self.updated_at, datetime):
            self.updated_at = datetime.utcnow()
