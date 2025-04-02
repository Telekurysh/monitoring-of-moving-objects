from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class SensorType(StrEnum):
    GPS = "gps"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    FUEL = "fuel"
    MOTION = "motion"
    ACCELEROMETER = "accelerometer"
    OTHER = "other"


class SensorStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    FAULTY = "faulty"
    UNKNOWN = "unknown"


class SensorBase(BaseModel):
    """Базовая модель датчика."""
    object_id: UUID = Field(..., description="ID объекта, к которому относится датчик")
    type: SensorType = Field(..., description="Тип датчика")
    location: str | None = Field(..., min_length=1, max_length=100, description="Местоположение датчика")
    status: SensorStatus = Field(default=SensorStatus.ACTIVE, description="Статус сенсора")


class SensorModel(SensorBase):
    """Полная модель датчика."""
    id: UUID = Field(default_factory=uuid4, description="ID датчика")
    created_at: datetime = Field(..., description="Дата и время создания записи с датчика")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)
