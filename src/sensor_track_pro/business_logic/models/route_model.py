from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from src.sensor_track_pro.business_logic.models.zone_model import Point


class RouteStatus(StrEnum):
    """Статусы маршрутов."""
    PLANNED = "planned"  # Запланирован
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"  # Завершен
    DELAYED = "delayed"  # Задержан
    CANCELLED = "cancelled"  # Отменен


class RoutePoint(BaseModel):
    """Точка маршрута."""
    point: Point = Field(..., description="Координаты точки маршрута")
    name: str | None = Field(None, description="Название точки маршрута")
    arrival_time: datetime | None = Field(None, description="Планируемое время прибытия")
    departure_time: datetime | None = Field(None, description="Планируемое время отправления")
    type: str | None = Field(None, description="Тип точки (старт, финиш, промежуточная)")


class RouteBase(BaseModel):
    """Базовые поля маршрута."""
    object_id: UUID = Field(..., description="ID объекта, для которого создан маршрут")
    start_time: datetime = Field(..., description="Время начала маршрута")
    end_time: datetime | None = Field(None, description="Время окончания маршрута")
    status: RouteStatus = Field(default=RouteStatus.PLANNED, description="Статус маршрута")
    name: str | None = Field(None, max_length=100, description="Название маршрута")
    description: str | None = Field(None, max_length=500, description="Описание маршрута")
    points: list[RoutePoint] = Field(default=[], description="Точки маршрута")
    metadata: dict[str, Any] | None = Field(None, description="Метаданные маршрута")


class RouteModel(RouteBase):
    """Полная модель маршрута."""
    id: UUID = Field(default_factory=uuid4, description="Уникальный идентификатор маршрута")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Дата и время создания маршрута")
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                 description="Дата и время последнего обновления маршрута")

    model_config = ConfigDict(from_attributes=True)
