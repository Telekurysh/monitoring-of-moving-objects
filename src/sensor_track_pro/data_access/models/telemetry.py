from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class Telemetry(Base):
    """Модель телеметрии в базе данных."""

    id: Mapped[uuid.UUID] = mapped_column(UUID[Any](as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id: Mapped[String] = mapped_column(ForeignKey("object.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    signal_strength: Mapped[float] = mapped_column(Float[Any], nullable=True)
    additional_metrics: Mapped[JSON] = mapped_column(nullable=True)  # Хранит дополнительные метрики в формате JSON

    # Связи
    object = relationship("Object", back_populates="telemetry")

    __table_args__ = (
        Index("idx_telemetry_object_time", "object_id", "timestamp"),
        Index("idx_telemetry_signal", "signal_strength"),
    )
