from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class TelemetryBase(BaseModel):
    """Базовые поля телеметрии."""

    object_id: UUID = Field(..., description="ID объекта")
    timestamp: datetime = Field(..., description="Временная метка")
    signal_strength: float | None = Field(None, ge=0.0, le=100.0, description="Уровень сигнала в процентах")
    additional_metrics: dict[str, Any] | None = Field(None,
                                                      description="Дополнительные метрики в формате ключ-значение")


class TelemetryModel(TelemetryBase):
    """Полная модель телеметрии."""

    id: UUID = Field(..., description="Уникальный идентификатор записи телеметрии")
    created_at: datetime = Field(..., description="Дата и время создания записи")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)
