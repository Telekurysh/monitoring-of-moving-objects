from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.models.event_model import EventBase
from src.sensor_track_pro.business_logic.models.event_model import EventModel


class IEventRepository(ABC):
    """Интерфейс репозитория для работы с событиями."""

    @abstractmethod
    async def create(self, event_data: EventBase) -> EventModel:
        """
        Создает новое событие.
        
        Args:
            event_data: Данные для создания события (без служебных полей)
            
        Returns:
            Созданное событие с заполненными служебными полями
        """

    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> EventModel | None:
        """
        Получает событие по его идентификатору.
        
        Args:
            event_id: UUID идентификатор события
            
        Returns:
            Событие, если найдено, иначе None
        """

    @abstractmethod
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            **filters: dict[str, Any]
    ) -> list[EventModel]:
        """
        Получает список событий с пагинацией и фильтрацией.
        
        Args:
            skip: Количество пропускаемых событий
            limit: Максимальное количество возвращаемых событий
            filters: Параметры фильтрации (sensor_id, event_type, timestamp и др.)
            
        Returns:
            Список событий
        """

    @abstractmethod
    async def update(
            self,
            event_id: UUID,
            event_data: dict[str, Any]
    ) -> EventModel | None:
        """
        Обновляет событие по идентификатору.
        
        Args:
            event_id: UUID идентификатор события
            event_data: Данные для частичного обновления
            
        Returns:
            Обновленное событие, если найдено, иначе None
        """

    @abstractmethod
    async def delete(self, event_id: UUID) -> bool:
        """
        Удаляет событие по идентификатору.
        
        Args:
            event_id: UUID идентификатор события
            
        Returns:
            True если удаление успешно, иначе False
        """

    @abstractmethod
    async def get_by_sensor_id(
            self,
            sensor_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> list[EventModel]:
        """
        Получает события, зафиксированные определенным сенсором.
        
        Args:
            sensor_id: UUID идентификатор сенсора
            skip: Количество пропускаемых событий
            limit: Максимальное количество возвращаемых событий
            
        Returns:
            Список событий
        """

    @abstractmethod
    async def get_by_time_range(
            self,
            start_time: datetime,
            end_time: datetime,
            skip: int = 0,
            limit: int = 100
    ) -> list[EventModel]:
        """
        Получает события за определенный временной период.
        
        Args:
            start_time: Начало временного периода
            end_time: Конец временного периода
            skip: Количество пропускаемых событий
            limit: Максимальное количество возвращаемых событий
            
        Returns:
            Список событий за указанный период
        """

    @abstractmethod
    async def get_by_coordinates(
            self,
            latitude: float,
            longitude: float,
            radius: float,
            skip: int = 0,
            limit: int = 100
    ) -> list[EventModel]:
        """
        Получает события в указанном радиусе от заданных координат.
        
        Args:
            latitude: Широта центральной точки
            longitude: Долгота центральной точки
            radius: Радиус поиска в километрах
            skip: Количество пропускаемых событий
            limit: Максимальное количество возвращаемых событий
            
        Returns:
            Список событий в заданном радиусе
        """
