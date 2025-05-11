from __future__ import annotations

import uuid

from sqlalchemy import Enum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.sensor_track_pro.business_logic.models.object_model import ObjectType
from src.sensor_track_pro.data_access.models.base import Base


class Object(Base):
    """Модель объекта мониторинга."""

    __tablename__ = "object"  # type: ignore

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[ObjectType] = mapped_column(Enum(ObjectType), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Связи с использованием строковых ссылок
    sensors = relationship("Sensor", back_populates="object", cascade="all, delete-orphan")
    telemetry = relationship("Telemetry", back_populates="object", cascade="all, delete-orphan")
    routes = relationship("Route", back_populates="object", cascade="all, delete-orphan")
    zones = relationship("Zone", secondary="object_zone", back_populates="objects")
    users = relationship("User", secondary="userobject", back_populates="objects")
