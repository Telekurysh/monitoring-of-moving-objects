from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.models.object_model import ObjectBase
from src.sensor_track_pro.business_logic.models.object_model import ObjectModel
from src.sensor_track_pro.business_logic.models.object_model import ObjectType


class IObjectRepository(ABC):
    """Интерфейс репозитория для работы с объектами."""

    @abstractmethod
    async def create(self, object_data: ObjectModel) -> ObjectModel:
        """
        Создает новый объект мониторинга.
        
        Args:
            object_data: Данные для создания объекта
            
        Returns:
            Созданный объект
        """

    @abstractmethod
    async def get_by_id(self, object_id: UUID) -> ObjectModel | None:
        """
        Получает объект по его идентификатору.
        
        Args:
            object_id: Идентификатор объекта
            
        Returns:
            Объект, если найден, иначе None
        """

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, **filters: Any) -> list[ObjectModel]:
        """
        Получает список объектов с пагинацией и фильтрацией.
        
        Args:
            skip: Количество пропускаемых объектов
            limit: Максимальное количество возвращаемых объектов
            filters: Параметры фильтрации
            
        Returns:
            Список объектов
        """

    @abstractmethod
    async def update(self, object_id: UUID, object_data: ObjectBase) -> ObjectModel | None:
        """
        Обновляет объект по идентификатору.
        
        Args:
            object_id: Идентификатор объекта
            object_data: Данные для обновления
            
        Returns:
            Обновленный объект, если найден, иначе None
        """

    @abstractmethod
    async def delete(self, object_id: UUID) -> bool:
        """
        Удаляет объект по идентификатору.
        
        Args:
            object_id: Идентификатор объекта
            
        Returns:
            True если удаление успешно, иначе False
        """

    @abstractmethod
    async def get_by_type(self, object_type: ObjectType, skip: int = 0, limit: int = 100) -> list[ObjectModel]:
        """
        Получает объекты определенного типа.
        
        Args:
            object_type: Тип объекта
            skip: Количество пропускаемых объектов
            limit: Максимальное количество возвращаемых объектов
            
        Returns:
            Список объектов указанного типа
        """

    @abstractmethod
    async def get_count(self, **filters: Any) -> int:
        """
        Получает количество объектов, соответствующих фильтрам.
        
        Args:
            filters: Параметры фильтрации
            
        Returns:
            Количество объектов
        """
