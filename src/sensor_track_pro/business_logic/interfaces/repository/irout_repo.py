from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.models.route_model import RouteBase
from src.sensor_track_pro.business_logic.models.route_model import RouteModel
from src.sensor_track_pro.business_logic.models.route_model import RouteStatus


class IRouteRepository(ABC):
    """Интерфейс репозитория для работы с маршрутами."""

    @abstractmethod
    async def create(self, route_data: RouteBase) -> RouteModel:
        """
        Создает новый маршрут.
        
        Args:
            route_data: Данные для создания маршрута (без служебных полей)
            
        Returns:
            Созданный маршрут с заполненными служебными полями
        """

    @abstractmethod
    async def get_by_id(self, route_id: UUID) -> RouteModel | None:
        """
        Получает маршрут по его идентификатору.
        
        Args:
            route_id: UUID идентификатор маршрута
            
        Returns:
            Маршрут, если найден, иначе None
        """

    @abstractmethod
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            **filters: dict[str, Any]
    ) -> list[RouteModel]:
        """
        Получает список маршрутов с пагинацией и фильтрацией.
        
        Args:
            skip: Количество пропускаемых маршрутов
            limit: Максимальное количество возвращаемых маршрутов
            filters: Параметры фильтрации (object_id, status, name)
            
        Returns:
            Список маршрутов
        """

    @abstractmethod
    async def update(
            self,
            route_id: UUID,
            route_data: dict[str, Any]
    ) -> RouteModel | None:
        """
        Обновляет маршрут по идентификатору.
        
        Args:
            route_id: UUID идентификатор маршрута
            route_data: Данные для частичного обновления
            
        Returns:
            Обновленный маршрут, если найден, иначе None
        """

    @abstractmethod
    async def delete(self, route_id: UUID) -> bool:
        """
        Удаляет маршрут по идентификатору.
        
        Args:
            route_id: UUID идентификатор маршрута
            
        Returns:
            True если удаление успешно, иначе False
        """

    @abstractmethod
    async def get_by_object_id(
            self,
            object_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> list[RouteModel]:
        """
        Получает маршруты определенного объекта.
        
        Args:
            object_id: UUID идентификатор объекта
            skip: Количество пропускаемых маршрутов
            limit: Максимальное количество возвращаемых маршрутов
            
        Returns:
            Список маршрутов объекта
        """

    @abstractmethod
    async def get_by_status(
            self,
            status: RouteStatus,
            skip: int = 0,
            limit: int = 100
    ) -> list[RouteModel]:
        """
        Получает маршруты с определенным статусом.
        
        Args:
            status: Статус маршрута из перечисления RouteStatus
            skip: Количество пропускаемых маршрутов
            limit: Максимальное количество возвращаемых маршрутов
            
        Returns:
            Список маршрутов с указанным статусом
        """

    @abstractmethod
    async def get_active_routes(
            self,
            skip: int = 0,
            limit: int = 100
    ) -> list[RouteModel]:
        """
        Получает активные маршруты (IN_PROGRESS).
        
        Args:
            skip: Количество пропускаемых маршрутов
            limit: Максимальное количество возвращаемых маршрутов
            
        Returns:
            Список активных маршрутов
        """

    @abstractmethod
    async def get_by_time_range(
            self,
            start_time: datetime,
            end_time: datetime,
            skip: int = 0,
            limit: int = 100
    ) -> list[RouteModel]:
        """
        Получает маршруты за определенный временной период.
        
        Args:
            start_time: Начало временного периода
            end_time: Конец временного периода
            skip: Количество пропускаемых маршрутов
            limit: Максимальное количество возвращаемых маршрутов
            
        Returns:
            Список маршрутов за указанный период
        """
