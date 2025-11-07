from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class ObjectZone(Base):
    """Модель связи объекта с зоной (история входа/выхода)."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        return "object_zone"

    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("objects.id"), primary_key=True)
    zone_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("zones.id"), primary_key=True)
    entered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    exited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    zone = relationship("Zone", backref="object_zones")

    __table_args__ = (
        UniqueConstraint("object_id", "zone_id", "entered_at"),
        Index("idx_object_zone", "object_id", "zone_id", "entered_at", "exited_at"),
    )