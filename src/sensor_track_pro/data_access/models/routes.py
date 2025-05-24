from __future__ import annotations

import uuid

from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base
from src.sensor_track_pro.business_logic.models.route_model import RouteStatus


class Route(Base):
    """Модель маршрута в базе данных."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        return "routes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("objects.id"), nullable=False)
    name: Mapped[str] = mapped_column()
    description = Column(String(500), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status: Mapped["RouteStatus"] = mapped_column(Enum(RouteStatus, name="route_status"), nullable=False, default="planned")
    points = Column(JSON, nullable=False)  # Хранит список точек маршрута
    route_metadata = Column("metadata", JSON, nullable=True)  # Дополнительные метаданные маршрута

    # Связи
    object = relationship("Object", back_populates="routes")

    __table_args__ = (
        Index("idx_route_object_time", "object_id", "start_time", "end_time"),
        Index("idx_route_status", "status"),
    )