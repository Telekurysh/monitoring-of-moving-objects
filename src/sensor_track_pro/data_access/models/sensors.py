from __future__ import annotations

import uuid

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class Sensor(Base):
    """Модель датчика."""

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id = Column(String(36), ForeignKey("object.id"), nullable=False)
    type: Mapped[str] = mapped_column(String)    # аннотация для type
    location = Column(String(100))
    status: Mapped[str] = mapped_column(String)  # аннотация для status

    # Связи
    object = relationship("Object", back_populates="sensors")
    events = relationship("Event", back_populates="sensor", cascade="all, delete-orphan")
