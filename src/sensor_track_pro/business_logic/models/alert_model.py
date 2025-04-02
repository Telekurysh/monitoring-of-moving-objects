from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class AlertType(StrEnum):
    """Типы оповещений."""

    ZONE_EXIT = "zone_exit"  # Выход из зоны
    ZONE_ENTER = "zone_enter"  # Вход в зону
    SPEED_VIOLATION = "speed_violation"  # Нарушение скоростного режима
    SENSOR_FAILURE = "sensor_failure"  # Сбой сенсора
    DISCONNECTION = "disconnection"  # Потеря связи
    CUSTOM = "custom"  # Пользовательское оповещение


class AlertSeverity(StrEnum):
    """Уровень важности оповещения."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertBase(BaseModel):
    """Базовые поля оповещения."""

    event_id: UUID = Field(..., description="ID события, вызвавшего оповещение")
    alert_type: AlertType = Field(..., description="Тип оповещения")
    severity: AlertSeverity = Field(..., description="Уровень важности оповещения")
    message: str = Field(..., min_length=1, max_length=500, description="Текст оповещения")
    timestamp: datetime = Field(..., description="Дата и время создания оповещения")


class AlertModel(AlertBase):
    """Поля модели оповещения."""
    id: UUID = Field(..., description="Уникальный идентификатор оповещения")
    created_at: datetime = Field(..., description="Дата и время создания оповещения")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)
