from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class ObjectZone(Base):
    """Модель связи объекта с зоной."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        return "object_zone"

    id: Mapped[uuid.UUID] = mapped_column(UUID[Any](as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)  # явное указание типа
    object_id: Mapped[uuid.UUID] = mapped_column(UUID[Any](as_uuid=True), ForeignKey("object.id"), primary_key=True)
    zone_id: Mapped[uuid.UUID] = mapped_column(UUID[Any](as_uuid=True), ForeignKey("zone.id"), primary_key=True)
    entered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    exited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    zone = relationship("Zone", backref="object_zones")

    __table_args__ = (
        UniqueConstraint("object_id", "zone_id", "entered_at"),
        Index("idx_object_zone", "object_id", "zone_id", "entered_at", "exited_at"),
    )