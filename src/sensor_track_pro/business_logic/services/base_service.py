from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import TypeVar

from src.sensor_track_pro.business_logic.models.common_types import FilterParams


T = TypeVar("T")


class BaseService[T](ABC):
    """Базовый класс для всех сервисов."""

    def __init__(self, repository: Any) -> None:
        self._repository = repository

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, **filters: FilterParams) -> list[T]:
        """Получить все сущности с пагинацией и фильтрацией."""
        raise NotImplementedError
