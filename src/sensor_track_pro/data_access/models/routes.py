from __future__ import annotations

import uuid

from typing import Any

from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class Route(Base):
    """Модель маршрута в базе данных."""

    id: Mapped[uuid.UUID] = mapped_column(UUID[Any](as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id = Column(String(36), ForeignKey("object.id"), nullable=False)
    name: Mapped[str] = mapped_column()
    description = Column(String(500), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PLANNED")
    points = Column(JSON, nullable=False)  # Хранит список точек маршрута
    route_metadata = Column(JSON, nullable=True)  # Дополнительные метаданные маршрута

    # Связи
    object = relationship("Object", back_populates="routes")

    __table_args__ = (
        Index("idx_route_object_time", "object_id", "start_time", "end_time"),
        Index("idx_route_status", "status"),
    )