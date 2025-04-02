from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from typing import Iterator
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import ValidationInfo
from pydantic import field_validator


# Constants for geographical coordinates
MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180
MIN_POLYGON_POINTS = 3


class ZoneType(StrEnum):
    """Типы зон."""
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"

    @classmethod
    def choices(cls) -> list[str]:
        return [member.value for member in cls]


@dataclass(frozen=True, order=True)
class Point:
    """Точка с координатами."""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

    def __hash__(self) -> int:
        return hash((self.latitude, self.longitude))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.latitude == other.latitude and self.longitude == other.longitude

    def __iter__(self) -> Iterator[float]:
        yield self.latitude
        yield self.longitude


class CircleZone(BaseModel):
    """Круглая зона."""
    center: Point = Field(..., description="Центр круга")
    radius: float = Field(..., description="Радиус круга (в метрах)")


class RectangleZone(BaseModel):
    """Прямоугольная зона."""
    top_left: Point = Field(..., description="Левый верхний угол прямоугольника")
    bottom_right: Point = Field(..., description="Правый нижний угол прямоугольника")

    def get_points(self) -> Iterator[Point]:
        yield self.top_left
        yield self.bottom_right


class PolygoneZone(BaseModel):
    """Многоугольная зона."""
    points: list[Point] = Field(..., description="Список точек многоугольника")

    @field_validator("points")
    @classmethod
    def validate_poligon_points(cls, v: list[Point]) -> list[Point]:
        """Проверяет валидность точек полигона"""
        if len(v) < MIN_POLYGON_POINTS:
            raise ValueError("Должно быть не менее 3 точек для создания многоугольника")
        unique_points = set(v)
        if len(unique_points) < MIN_POLYGON_POINTS:
            raise ValueError("Точки многоугольника должны быть уникальными")
        for point in unique_points:
            if not isinstance(point, Point):
                raise ValueError("Все точки должны быть экземплярами класса Point")
            if not (MIN_LATITUDE <= point.latitude <= MAX_LATITUDE):
                raise ValueError("Широта должна быть в диапазоне от -90 до 90")
            if not (MIN_LONGITUDE <= point.longitude <= MAX_LONGITUDE):
                raise ValueError("Долгота должна быть в диапазоне от -180 до 180")
        return v


class ZoneBase(BaseModel):
    """Базовая модель зоны."""

    name: str = Field(..., min_length=1, max_length=100, description="Название зоны")
    zone_type: ZoneType = Field(..., description="Тип зоны")
    coordiates: CircleZone | RectangleZone | PolygoneZone = Field(..., description="Координаты зоны")
    description: str | None = Field(None, max_length=500, description="Описание зоны")


class ZoneModel(ZoneBase):
    """Полная модель зоны."""

    id: UUID = Field(..., description="Уникальный идентификатор зоны")
    created_at: datetime = Field(..., description="Дата и время создания зоны")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления зоны")

    @field_validator("zone_type")
    @classmethod
    def validate_zone_type(cls, value: str, info: ValidationInfo) -> str:
        """Валидирует тип зоны."""
        if value not in ZoneType.choices():
            raise ValueError(f"Invalid zone type: {value}")
        return value

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, value: CircleZone | RectangleZone | PolygoneZone,
                             info: ValidationInfo) -> CircleZone | RectangleZone | PolygoneZone:
        """Валидирует координаты зоны."""
        if not isinstance(value, (CircleZone, RectangleZone, PolygoneZone)):
            raise ValueError(f"Invalid coordinates type: {type(value)}")
        return value

    model_config = ConfigDict(from_attributes=True)
