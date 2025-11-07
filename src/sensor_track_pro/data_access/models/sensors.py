from __future__ import annotations

import uuid

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Enum

from src.sensor_track_pro.data_access.models.base import Base
from src.sensor_track_pro.business_logic.models.sensor_model import SensorType, SensorStatus


class Sensor(Base):
    """Модель датчика."""

    @declared_attr.directive
    def __tablename__(self) -> str:
        return "sensors"

    id: Mapped[uuid.UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id = Column(pgUUID(as_uuid=True), ForeignKey("objects.id"), nullable=False)  # исправлено имя таблицы
    sensor_type: Mapped[SensorType] = mapped_column("sensor_type", Enum(SensorType, name="sensor_type"), nullable=False)
    location = Column(String(100))
    sensor_status: Mapped[SensorStatus] = mapped_column("sensor_status", Enum(SensorStatus, name="sensor_status"), nullable=False)
    latitude: Mapped[float | None] = mapped_column("latitude", nullable=True)
    longitude: Mapped[float | None] = mapped_column("longitude", nullable=True)

    # Добавляем свойства для поддержки alias в Pydantic модели
    @property
    def type(self) -> SensorType:
        return self.sensor_type

    @property
    def status(self) -> SensorStatus:
        return self.sensor_status

    # Связи
    object = relationship("Object", back_populates="sensors")
    events = relationship("Event", back_populates="sensor", cascade="all, delete-orphan")
