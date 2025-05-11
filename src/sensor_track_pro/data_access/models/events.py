from __future__ import annotations

import uuid

from datetime import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class Event(Base):
    """Модель события в системе."""

    id: Mapped[uuid.UUID] = mapped_column(UUID[Any](as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(String(36), ForeignKey("sensor.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    details = Column(String(500), nullable=True)
    location: Mapped[str] = mapped_column()  # теперь используется mapped_column

    # Связи
    sensor = relationship("Sensor", back_populates="events")
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_event_sensor_timestamp", "sensor_id", "timestamp"),
    )