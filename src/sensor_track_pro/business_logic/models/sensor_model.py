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
    FUEL = "fuel"
    OTHER = "other"


class SensorStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
   

class SensorBase(BaseModel):
    """Базовая модель датчика."""
    object_id: UUID = Field(..., description="ID объекта, к которому относится датчик")
    sensor_type: SensorType = Field(..., alias="type", description="Тип датчика")
    location: str | None = Field(..., min_length=1, max_length=100, description="Местоположение датчика")
    sensor_status: SensorStatus = Field(default=SensorStatus.ACTIVE, alias="status", description="Статус сенсора")


class SensorModel(SensorBase):
    """Полная модель датчика."""
    id: UUID = Field(default_factory=uuid4, description="ID датчика")
    created_at: datetime = Field(..., description="Дата и время создания записи с датчика")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)
