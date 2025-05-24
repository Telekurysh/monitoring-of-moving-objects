from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class Telemetry(Base):
    """Модель телеметрии в базе данных."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        return "telemetry"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("objects.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    signal_strength: Mapped[float | None] = mapped_column(Float, nullable=True)
    additional_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Связи
    object = relationship("Object", back_populates="telemetry")

    __table_args__ = (
        Index("idx_telemetry_object_time", "object_id", "timestamp"),
        Index("idx_telemetry_signal", "signal_strength"),
    )
