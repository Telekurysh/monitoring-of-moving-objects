from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from enum import StrEnum
from uuid import UUID
from uuid import uuid4

from pydantic import BaseModel
from pydantic import Field


class ZoneType(StrEnum):
    """Типы геозон"""
    CIRCLE = "circle"
    RECTANGLE = "rectangle"


class CircleCoordinates(BaseModel):
    """Координаты для круговой зоны"""
    center: tuple[float, float]  # (latitude, longitude)
    radius: float  # в метрах


class RectangleCoordinates(BaseModel):
    """Координаты для прямоугольной зоны"""
    top_left: tuple[float, float]
    bottom_right: tuple[float, float]


class ZoneBase(BaseModel):
    """Базовая модель зоны без ID"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    type: ZoneType
    coordinates: CircleCoordinates | RectangleCoordinates
    is_active: bool = Field(default=True)


class ZoneCreate(ZoneBase):
    """Модель для создания зоны"""


class ZoneUpdate(BaseModel):
    """Модель для обновления зоны"""
    id: UUID | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    coordinates: CircleCoordinates | RectangleCoordinates | None = None
    is_active: bool | None = None


class ZoneBoundary(ZoneBase):
    """Полная модель зоны с ID"""
    id: UUID = Field(default_factory=uuid4)


class IZoneRepository(ABC):
    """Абстрактный репозиторий для работы с геозонами"""

    @abstractmethod
    async def get_zones_for_object(self, object_id: UUID) -> list[ZoneBoundary]:
        """Получить все зоны для объекта"""
        raise NotImplementedError

    @abstractmethod
    async def get_zone_by_id(self, zone_id: UUID) -> ZoneBoundary | None:
        """Найти зону по ID"""
        raise NotImplementedError

    @abstractmethod
    async def create_zone(self, zone_data: ZoneCreate) -> ZoneBoundary:
        """Создать новую зону"""
        raise NotImplementedError

    @abstractmethod
    async def update_zone(
            self,
            zone_id: UUID,
            zone_data: ZoneUpdate
    ) -> ZoneBoundary | None:
        """Обновить существующую зону"""
        raise NotImplementedError

    @abstractmethod
    async def delete_zone(self, zone_id: UUID) -> bool:
        """Удалить зону"""
        raise NotImplementedError
