from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from pydantic import BeforeValidator
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator
from pydantic_core.core_schema import ValidationInfo


class MetricType(StrEnum):
    """Типы метрик телеметрии"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    FUEL_LEVEL = "fuel_level"
    SPEED = "speed"
    CUSTOM = "custom"


def validate_decimal(v: float) -> float:
    """Конвертация в float с проверкой"""
    if isinstance(v, Decimal):
        return float(v)
    return v


MIN_TEMPERATURE = -273  # Абсолютный ноль
MAX_TEMPERATURE = 1000  # Максимальная допустимая температура
MIN_FUEL_LEVEL = 0  # Минимальный уровень топлива
MAX_FUEL_LEVEL = 100  # Максимальный уровень топлива (в процентах)


class TelemetryData(BaseModel):
    """Модель данных телеметрии"""
    model_config = ConfigDict(use_enum_values=True)

    object_id: UUID
    metric_type: MetricType
    value: Annotated[float, BeforeValidator(validate_decimal)]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sensor_id: UUID | None = None
    additional_data: dict[str, str] = Field(default_factory=dict)

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: float, info: ValidationInfo) -> float:
        """Валидация значений в зависимости от типа метрики"""
        metric_type = info.data.get('metric_type')

        if metric_type == MetricType.TEMPERATURE and not (MIN_TEMPERATURE <= v <= MAX_TEMPERATURE):
            raise ValueError("Temperature must be between -273 and 1000")
        if metric_type == MetricType.SPEED and v < 0:
            raise ValueError("Speed cannot be negative")
        if metric_type == MetricType.FUEL_LEVEL and not (MIN_FUEL_LEVEL <= v <= MAX_FUEL_LEVEL):
            raise ValueError("Fuel level must be between 0 and 100%")

        return round(v, 2)


MAX_LATITUDE = 90  # Максимальное значение широты
MAX_LONGITUDE = 180  # Максимальное значение долготы


class PositionData(BaseModel):
    """Модель данных о местоположении"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    object_id: UUID
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: float | None = Field(None, ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    accuracy: float = Field(1.0, ge=0)

    @model_validator(mode='after')
    def validate_coordinates(self) -> PositionData:
        """Комплексная проверка координат"""
        if abs(self.latitude) > MAX_LATITUDE:
            raise ValueError("Latitude must be between -90 and 90")
        if abs(self.longitude) > MAX_LONGITUDE:
            raise ValueError("Longitude must be between -180 and 180")
        return self


class TelemetryFilter(BaseModel):
    """Фильтр для запроса телеметрии"""
    object_id: UUID | None = None
    metric_type: MetricType | None = None
    time_range: tuple[datetime, datetime] | None = None
    limit: int = Field(100, gt=0, le=1000)

    @model_validator(mode='after')
    def validate_time_range(self) -> TelemetryFilter:
        """Проверка временного диапазона"""
        if self.time_range and self.time_range[0] > self.time_range[1]:
            raise ValueError("Start time must be before end time")
        return self


class ITelemetryRepository(ABC):
    """Абстрактный репозиторий для работы с телеметрией"""

    @abstractmethod
    async def save_telemetry(self, data: TelemetryData) -> None:
        """Сохранить данные телеметрии"""
        raise NotImplementedError

    @abstractmethod
    async def save_position(self, data: PositionData) -> None:
        """Сохранить данные о местоположении"""
        raise NotImplementedError

    @abstractmethod
    async def get_latest_telemetry(
            self,
            object_id: UUID,
            metric_type: MetricType
    ) -> TelemetryData | None:
        """Получить последнее значение метрики для объекта"""
        raise NotImplementedError

    @abstractmethod
    async def get_latest_position(self, object_id: UUID) -> PositionData | None:
        """Получить последнее известное местоположение объекта"""
        raise NotImplementedError

    @abstractmethod
    async def get_telemetry_history(
            self,
            telemetry_filter: TelemetryFilter
    ) -> list[TelemetryData]:
        """Получить историю телеметрии по фильтру"""
        raise NotImplementedError

    @abstractmethod
    async def get_position_history(
            self,
            object_id: UUID,
            time_range: tuple[datetime, datetime] | None = None,
            limit: int = 100
    ) -> list[PositionData]:
        """Получить историю перемещений объекта"""
        raise NotImplementedError
