from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class EventType(StrEnum):
    """Типы событий."""
    MOVE = "move"
    STOP = "stop"
    ZONE_ENTER = "zone_enter"  # исправлено с zone_entr
    ZONE_EXIT = "zone_exit"
    SPEED_LIMIT = "speed_limit"
    SENSOR_FAULT = "sensor_fault"
    OTHER = "other"


class EventBase(BaseModel):
    """Базовая модель события."""
    sensor_id: UUID = Field(..., description="ID датчика, зафиксировавшего событие")
    timestamp: datetime = Field(..., description="Дата и время события")
    latitude: float = Field(..., description="Широта события")
    longitude: float = Field(..., description="Долгота события")
    speed: float | None = Field(..., description="Скорость события")
    event_type: EventType = Field(..., description="Тип события")
    details: str | None = Field(None, max_length=500, description="Дополнительные детали события")


class EventModel(EventBase):
    """Полная модель события."""

    id: UUID = Field(..., description="Уникальный идентификатор события")  # исправлено с int на UUID
    created_at: datetime = Field(..., description="Дата и время создания записи о событии")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)
