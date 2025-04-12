from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from src.sensor_track_pro.business_logic.models.event_model import EventType
from src.sensor_track_pro.data_access.models.base import Base


class Event(Base):
    """Модель события в системе."""

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(36), ForeignKey("sensor.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    details = Column(String(500), nullable=True)

    # Связи
    sensor = relationship("Sensor", back_populates="events")
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_event_sensor_timestamp", "sensor_id", "timestamp"),
    )