from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ObjectType(StrEnum):
    """Типы отслеживаемых объектов."""
    VEHICLE = "vehicle"  # исправлено с VEIHICLE
    CARGO = "cargo"
    EQUIPMENT = "equipment"
    OTHER = "other"


class ObjectBase(BaseModel):
    """Базовая модель объекта."""
    name: str = Field(..., min_length=1, max_length=100, description="Название объекта")
    type: ObjectType = Field(..., description="Тип объекта")
    description: str | None = Field(None, max_length=500, description="Описание объекта")


class ObjectModel(ObjectBase):
    """Полная модель объекта."""
    id: UUID = Field(default_factory=uuid4, description="ID объекта")
    created_at: datetime = Field(..., description="Дата и время создания объекта")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления объекта")

    model_config = ConfigDict(from_attributes=True)
