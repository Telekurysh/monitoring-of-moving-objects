from __future__ import annotations

from typing import Any
from typing import TypeVar

from src.sensor_track_pro.business_logic.models.common_types import FilterParams


T = TypeVar("T")


class BaseService[T]:
    """Базовый класс для всех сервисов."""

    def __init__(self, repository: Any) -> None:
        self._repository = repository

    async def get_all(self, skip: int = 0, limit: int = 100, **filters: FilterParams) -> list[T]:
        return await self._repository.get_all(skip, limit, **filters)
