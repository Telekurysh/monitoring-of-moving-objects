from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class Telemetry(Base):
    """Модель телеметрии в базе данных."""

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    object_id = Column(String(36), ForeignKey("object.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    signal_strength = Column(Float, nullable=True)
    additional_metrics = Column(JSON, nullable=True)  # Хранит дополнительные метрики в формате JSON

    # Связи
    object = relationship("Object", back_populates="telemetry")

    __table_args__ = (
        Index("idx_telemetry_object_time", "object_id", "timestamp"),
        Index("idx_telemetry_signal", "signal_strength"),
    )
