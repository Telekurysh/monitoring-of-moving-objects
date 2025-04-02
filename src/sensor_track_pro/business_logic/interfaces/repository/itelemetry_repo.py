from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.models.telemetry_model import TelemetryBase
from src.sensor_track_pro.business_logic.models.telemetry_model import TelemetryModel


class ITelemetryRepository(ABC):
    """Интерфейс репозитория для работы с телеметрией."""

    @abstractmethod
    async def create(self, telemetry_data: TelemetryBase) -> TelemetryModel:
        """
        Создает новую запись телеметрии.
        
        Args:
            telemetry_data: Данные для создания записи (без служебных полей)
            
        Returns:
            Созданная запись телеметрии с заполненными служебными полями
        """

    @abstractmethod
    async def get_by_id(self, telemetry_id: UUID) -> TelemetryModel | None:
        """
        Получает запись телеметрии по её идентификатору.
        
        Args:
            telemetry_id: UUID идентификатор записи
            
        Returns:
            Запись телеметрии, если найдена, иначе None
        """

    @abstractmethod
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            **filters: dict[str, Any]
    ) -> list[TelemetryModel]:
        """
        Получает список записей телеметрии с пагинацией и фильтрацией.
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            filters: Параметры фильтрации (object_id, timestamp, signal_strength)
            
        Returns:
            Список записей телеметрии
        """

    @abstractmethod
    async def update(
            self,
            telemetry_id: UUID,
            telemetry_data: dict[str, Any]
    ) -> TelemetryModel | None:
        """
        Обновляет запись телеметрии по идентификатору.
        
        Args:
            telemetry_id: UUID идентификатор записи
            telemetry_data: Данные для частичного обновления
            
        Returns:
            Обновленная запись телеметрии, если найдена, иначе None
        """

    @abstractmethod
    async def delete(self, telemetry_id: UUID) -> bool:
        """
        Удаляет запись телеметрии по идентификатору.
        
        Args:
            telemetry_id: UUID идентификатор записи
            
        Returns:
            True если удаление успешно, иначе False
        """

    @abstractmethod
    async def get_by_object_id(
            self,
            object_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> list[TelemetryModel]:
        """
        Получает телеметрию определенного объекта.
        
        Args:
            object_id: Числовой идентификатор объекта
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            
        Returns:
            Список записей телеметрии объекта
        """

    @abstractmethod
    async def get_by_time_range(
            self,
            start_time: datetime,
            end_time: datetime,
            skip: int = 0,
            limit: int = 100
    ) -> list[TelemetryModel]:
        """
        Получает телеметрию за определенный временной период.
        
        Args:
            start_time: Начало временного периода
            end_time: Конец временного периода
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            
        Returns:
            Список записей телеметрии за указанный период
        """

    @abstractmethod
    async def get_by_signal_strength(
            self,
            min_strength: float,
            max_strength: float,
            skip: int = 0,
            limit: int = 100
    ) -> list[TelemetryModel]:
        """
        Получает телеметрию с уровнем сигнала в заданном диапазоне.
        
        Args:
            min_strength: Минимальный уровень сигнала (0.0-100.0)
            max_strength: Максимальный уровень сигнала (0.0-100.0)
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            
        Returns:
            Список записей телеметрии, удовлетворяющих условию
        """
