from __future__ import annotations

from uuid import uuid4

from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.orm import relationship

from src.sensor_track_pro.business_logic.models.route_model import RouteStatus
from src.sensor_track_pro.data_access.models.base import Base


class Route(Base):
    """Модель маршрута в базе данных."""

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    object_id = Column(String(36), ForeignKey("object.id"), nullable=False)
    name = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(Enum(RouteStatus), nullable=False, default=RouteStatus.PLANNED)
    points = Column(JSON, nullable=False)  # Хранит список точек маршрута
    metadata = Column(JSON, nullable=True)  # Дополнительные метаданные маршрута

    # Связи
    object = relationship("Object", back_populates="routes")

    __table_args__ = (
        Index("idx_route_object_time", "object_id", "start_time", "end_time"),
        Index("idx_route_status", "status"),
    )