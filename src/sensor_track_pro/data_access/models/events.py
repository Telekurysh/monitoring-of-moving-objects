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
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Enum

from src.sensor_track_pro.data_access.models.base import Base
from src.sensor_track_pro.business_logic.models.event_model import EventType


class Event(Base):
    """Модель события в системе."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        return "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sensors.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType, name="event_type", create_constraint=False), nullable=False)
    details = Column(String(500), nullable=True)

    # Связи
    sensor = relationship("Sensor", back_populates="events")
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_event_sensor_timestamp", "sensor_id", "timestamp"),
    )