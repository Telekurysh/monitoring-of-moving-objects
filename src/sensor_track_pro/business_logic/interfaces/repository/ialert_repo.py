from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.models.alert_model import AlertBase
from src.sensor_track_pro.business_logic.models.alert_model import AlertModel
from src.sensor_track_pro.business_logic.models.alert_model import AlertSeverity
from src.sensor_track_pro.business_logic.models.alert_model import AlertType


class IAlertRepository(ABC):
    """Интерфейс репозитория для работы с оповещениями."""

    @abstractmethod
    async def create(self, alert_data: AlertBase) -> AlertModel:
        """
        Создает новое оповещение.
        
        Args:
            alert_data: Данные для создания оповещения (без служебных полей)
            
        Returns:
            Созданное оповещение с заполненными служебными полями
        """

    @abstractmethod
    async def get_by_id(self, alert_id: UUID) -> AlertModel | None:
        """
        Получает оповещение по его идентификатору.
        
        Args:
            alert_id: UUID идентификатор оповещения
            
        Returns:
            Оповещение, если найдено, иначе None
        """

    @abstractmethod
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            **filters: dict[str, Any]
    ) -> list[AlertModel]:
        """
        Получает список оповещений с пагинацией и фильтрацией.
        
        Args:
            skip: Количество пропускаемых оповещений
            limit: Максимальное количество возвращаемых оповещений
            filters: Параметры фильтрации (event_id, alert_type, severity)
            
        Returns:
            Список оповещений
        """

    @abstractmethod
    async def update(
            self,
            alert_id: UUID,
            alert_data: dict[str, Any]
    ) -> AlertModel | None:
        """
        Обновляет оповещение по идентификатору.
        
        Args:
            alert_id: UUID идентификатор оповещения
            alert_data: Данные для частичного обновления
            
        Returns:
            Обновленное оповещение, если найдено, иначе None
        """

    @abstractmethod
    async def delete(self, alert_id: UUID) -> bool:
        """
        Удаляет оповещение по идентификатору.
        
        Args:
            alert_id: UUID идентификатор оповещения
            
        Returns:
            True если удаление успешно, иначе False
        """

    @abstractmethod
    async def get_by_event_id(self, event_id: UUID) -> list[AlertModel]:
        """
        Получает оповещения по идентификатору события.
        
        Args:
            event_id: UUID идентификатор события
            
        Returns:
            Список связанных оповещений
        """

    @abstractmethod
    async def get_by_severity(
            self,
            severity: AlertSeverity,
            skip: int = 0,
            limit: int = 100
    ) -> list[AlertModel]:
        """
        Получает оповещения определенной важности.
        
        Args:
            severity: Уровень важности из перечисления AlertSeverity
            skip: Количество пропускаемых оповещений
            limit: Максимальное количество возвращаемых оповещений
            
        Returns:
            Список оповещений указанного уровня важности
        """

    @abstractmethod
    async def get_by_type(
            self,
            alert_type: AlertType,
            skip: int = 0,
            limit: int = 100
    ) -> list[AlertModel]:
        """
        Получает оповещения определенного типа.
        
        Args:
            alert_type: Тип оповещения из перечисления AlertType
            skip: Количество пропускаемых оповещений
            limit: Максимальное количество возвращаемых оповещений
            
        Returns:
            Список оповещений указанного типа
        """

    @abstractmethod
    async def get_by_time_range(
            self,
            start_time: datetime,
            end_time: datetime,
            skip: int = 0,
            limit: int = 100
    ) -> list[AlertModel]:
        """
        Получает оповещения за определенный временной период.
        
        Args:
            start_time: Начало временного периода
            end_time: Конец временного периода
            skip: Количество пропускаемых оповещений
            limit: Максимальное количество возвращаемых оповещений
            
        Returns:
            Список оповещений за указанный период
        """
