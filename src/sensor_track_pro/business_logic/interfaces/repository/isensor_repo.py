from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.models.sensor_model import SensorBase
from src.sensor_track_pro.business_logic.models.sensor_model import SensorModel
from src.sensor_track_pro.business_logic.models.sensor_model import SensorStatus
from src.sensor_track_pro.business_logic.models.sensor_model import SensorType


class ISensorRepository(ABC):
    """Интерфейс репозитория для работы с сенсорами."""

    @abstractmethod
    async def create(self, sensor_data: SensorBase) -> SensorModel:
        """
        Создает новый сенсор.
        
        Args:
            sensor_data: Данные для создания сенсора (без служебных полей)
            
        Returns:
            Созданный сенсор с заполненными служебными полями
        """

    @abstractmethod
    async def get_by_id(self, sensor_id: UUID) -> SensorModel | None:
        """
        Получает сенсор по его идентификатору.
        
        Args:
            sensor_id: UUID идентификатор сенсора
            
        Returns:
            Сенсор, если найден, иначе None
        """

    @abstractmethod
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            **filters: dict[str, Any]
    ) -> list[SensorModel]:
        """
        Получает список сенсоров с пагинацией и фильтрацией.
        
        Args:
            skip: Количество пропускаемых сенсоров
            limit: Максимальное количество возвращаемых сенсоров
            filters: Параметры фильтрации (например, type, status, object_id)
            
        Returns:
            Список сенсоров
        """

    @abstractmethod
    async def update(
            self,
            sensor_id: UUID,
            sensor_data: dict[str, Any]
    ) -> SensorModel | None:
        """
        Обновляет сенсор по идентификатору.
        
        Args:
            sensor_id: UUID идентификатор сенсора
            sensor_data: Данные для обновления (частичное обновление)
            
        Returns:
            Обновленный сенсор, если найден, иначе None
        """

    @abstractmethod
    async def delete(self, sensor_id: UUID) -> bool:
        """
        Удаляет сенсор по идентификатору.
        
        Args:
            sensor_id: UUID идентификатор сенсора
            
        Returns:
            True если удаление успешно, иначе False
        """

    @abstractmethod
    async def get_by_object_id(
            self,
            object_id: UUID,
            skip: int = 0,
            limit: int = 100
    ) -> list[SensorModel]:
        """
        Получает сенсоры, установленные на определенном объекте.
        
        Args:
            object_id: UUID идентификатор объекта
            skip: Количество пропускаемых сенсоров
            limit: Максимальное количество возвращаемых сенсоров
            
        Returns:
            Список сенсоров
        """

    @abstractmethod
    async def get_by_type(
            self,
            sensor_type: SensorType,
            skip: int = 0,
            limit: int = 100
    ) -> list[SensorModel]:
        """
        Получает сенсоры определенного типа.
        
        Args:
            sensor_type: Тип сенсора из перечисления SensorType
            skip: Количество пропускаемых сенсоров
            limit: Максимальное количество возвращаемых сенсоров
            
        Returns:
            Список сенсоров указанного типа
        """

    @abstractmethod
    async def get_by_status(
            self,
            status: SensorStatus,
            skip: int = 0,
            limit: int = 100
    ) -> list[SensorModel]:
        """
        Получает сенсоры в определенном статусе.
        
        Args:
            status: Статус сенсора из перечисления SensorStatus
            skip: Количество пропускаемых сенсоров
            limit: Максимальное количество возвращаемых сенсоров
            
        Returns:
            Список сенсоров в указанном статусе
        """
