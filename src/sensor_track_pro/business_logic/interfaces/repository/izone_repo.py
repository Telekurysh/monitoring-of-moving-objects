from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.models.zone_model import ZoneBase
from src.sensor_track_pro.business_logic.models.zone_model import ZoneModel
from src.sensor_track_pro.business_logic.models.zone_model import ZoneType


class IZoneRepository(ABC):
    """Интерфейс репозитория для работы с зонами мониторинга."""

    @abstractmethod
    async def create(self, zone_data: ZoneBase) -> ZoneModel:
        """
        Создает новую зону мониторинга.
        
        Args:
            zone_data: Данные для создания зоны (без служебных полей)
            
        Returns:
            Созданная зона с заполненными служебными полями
        """

    @abstractmethod
    async def get_by_id(self, zone_id: UUID) -> ZoneModel | None:
        """
        Получает зону по её идентификатору.
        
        Args:
            zone_id: UUID идентификатор зоны
            
        Returns:
            Зона, если найдена, иначе None
        """

    @abstractmethod
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            **filters: dict[str, Any]
    ) -> list[ZoneModel]:
        """
        Получает список зон с пагинацией и фильтрацией.
        
        Args:
            skip: Количество пропускаемых зон
            limit: Максимальное количество возвращаемых зон
            filters: Параметры фильтрации (name, zone_type, description)
            
        Returns:
            Список зон
        """

    @abstractmethod
    async def update(
            self,
            zone_id: UUID,
            zone_data: dict[str, Any]
    ) -> ZoneModel | None:
        """
        Обновляет зону по идентификатору.
        
        Args:
            zone_id: UUID идентификатор зоны
            zone_data: Данные для частичного обновления
            
        Returns:
            Обновленная зона, если найдена, иначе None
        """

    @abstractmethod
    async def delete(self, zone_id: UUID) -> bool:
        """
        Удаляет зону по идентификатору.
        
        Args:
            zone_id: UUID идентификатор зоны
            
        Returns:
            True если удаление успешно, иначе False
        """

    @abstractmethod
    async def get_by_type(
            self,
            zone_type: ZoneType,
            skip: int = 0,
            limit: int = 100
    ) -> list[ZoneModel]:
        """
        Получает зоны определенного типа.
        
        Args:
            zone_type: Тип зоны из перечисления ZoneType
            skip: Количество пропускаемых зон
            limit: Максимальное количество возвращаемых зон
            
        Returns:
            Список зон указанного типа
        """

    @abstractmethod
    async def get_zones_containing_point(
            self,
            latitude: float,
            longitude: float
    ) -> list[ZoneModel]:
        """
        Получает зоны, содержащие указанную точку.
        
        Args:
            latitude: Широта точки
            longitude: Долгота точки
            
        Returns:
            Список зон, содержащих точку
        """

    @abstractmethod
    async def get_zones_for_object(
            self,
            object_id: UUID
    ) -> list[ZoneModel]:
        """
        Получает зоны, связанные с определенным объектом.
        
        Args:
            object_id: UUID идентификатор объекта
            
        Returns:
            Список зон объекта
        """
