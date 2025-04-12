# ruff: noqa: UP046
from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.data_access.models.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый класс для всех репозиториев."""

    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self._session = session
        self._model = model

    async def create(self, instance: ModelType) -> ModelType:
        """
        Создает новую запись в базе данных.
        
        Args:
            instance: Экземпляр модели для создания
            
        Returns:
            Созданный экземпляр с заполненными полями
        """
        try:
            self._session.add(instance)
            await self._session.flush()
            await self._session.refresh(instance)
            return instance
        except Exception as e:
            # Обработка ошибки создания записи: меняем сообщение для зоны
            if self._model.__name__ == "Zone":
                raise Exception(f"Ошибка создания зоны: {e}")
            raise Exception(f"Ошибка создания экземпляра: {e}")

    async def get_by_id(self, instance_id: UUID) -> ModelType | None:
        """
        Получает запись по идентификатору.
        
        Args:
            instance_id: UUID идентификатор записи
            
        Returns:
            Найденная запись или None
        """
        query = select(self._model).filter(self._model.id == str(instance_id))
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: dict[str, Any]
    ) -> list[ModelType]:
        """
        Получает список записей с пагинацией и фильтрацией.
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            filters: Параметры фильтрации
            
        Returns:
            Список записей
        """
        query = select(self._model)
        
        # Применяем фильтры
        for field, value in filters.items():
            if hasattr(self._model, field):
                query = query.filter(getattr(self._model, field) == value)
                
        query = query.offset(skip).limit(limit)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(self, instance_id: UUID, values: dict[str, Any]) -> ModelType | None:
        """
        Обновляет запись по идентификатору.
        
        Args:
            instance_id: UUID идентификатор записи
            values: Словарь с обновляемыми полями
            
        Returns:
            Обновленная запись или None
        """
        try:
            instance = await self.get_by_id(instance_id)
            if instance:
                for field, value in values.items():
                    if hasattr(instance, field):
                        setattr(instance, field, value)
                await self._session.flush()
                await self._session.refresh(instance)
                return instance
            return None
        except Exception as e:
            raise Exception(f"Ошибка обновления экземпляра с id {instance_id}: {e}")

    async def delete(self, instance_id: UUID) -> bool:
        """
        Удаляет запись по идентификатору.
        
        Args:
            instance_id: UUID идентификатор записи
            
        Returns:
            True если удаление успешно, иначе False
        """
        try:
            instance = await self.get_by_id(instance_id)
            if instance:
                await self._session.delete(instance)
                await self._session.flush()
                return True
            return False
        except Exception as e:
            raise Exception(f"Ошибка удаления экземпляра с id {instance_id}: {e}")

    async def exists(self, instance_id: UUID) -> bool:
        """
        Проверяет существование записи.
        
        Args:
            instance_id: UUID идентификатор записи
            
        Returns:
            True если запись существует, иначе False
        """
        query = select(self._model).filter(self._model.id == str(instance_id))
        result = await self._session.execute(query)
        return result.scalar_one_or_none() is not None
