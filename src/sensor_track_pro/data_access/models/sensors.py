from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class Sensor(Base):
    """Модель датчика."""

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    object_id = Column(String(36), ForeignKey("object.id"), nullable=False)
    type: Mapped[str] = mapped_column(String)    # аннотация для type
    location = Column(String(100))
    status: Mapped[str] = mapped_column(String)  # аннотация для status

    # Связи
    object = relationship("Object", back_populates="sensors")
    events = relationship("Event", back_populates="sensor", cascade="all, delete-orphan")
