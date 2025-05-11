# ruff: noqa: UP046
from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import Generator
from typing import Generic
from typing import TypeVar
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import exists
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
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
            # Собираем данные из колонок модели с преобразованием datetime к наивному формату
            data = {}
            for col in self._model.__table__.c:  # изменено: .columns -> .c
                value = getattr(instance, col.name)
                if isinstance(value, datetime) and value.tzinfo is not None:
                    value = value.replace(tzinfo=None)
                data[col.name] = value
            stmt = insert(self._model).values(**data).returning(*self._model.__table__.columns)
            result = await self._session.execute(stmt)
            row = result.fetchone()
            await self._session.commit()
            if row is None:
                raise Exception("Insert failed")
            pk = next(iter(self._model.__table__.primary_key)).name  # изменено
            pk_idx = list(result.keys()).index(pk)
            created_instance = await self.get_by_id(row[pk_idx])
            if created_instance is None:
                raise Exception("Insert failed: created instance is None")
            return created_instance
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
        query = select(self._model).where(self._model.id == instance_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None
    ) -> list[ModelType]:
        """
        Получает список записей с пагинацией и фильтрацией.
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            filters: Словарь параметров фильтрации
            
        Returns:
            Список записей
        """
        query = select(self._model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self._model, field):
                    query = query.where(getattr(self._model, field) == value)
                
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
            from datetime import datetime  # ensure import
            values_to_update = {}
            for key, value in values.items():
                if isinstance(value, datetime) and value.tzinfo is not None:
                    value = value.replace(tzinfo=None)
                values_to_update[key] = value
            # Добавляем автоматическое обновление updated_at, если не задано
            if "updated_at" not in values_to_update:
                values_to_update["updated_at"] = datetime.now().replace(tzinfo=None)
            stmt = (
                update(self._model)
                .where(self._model.id == instance_id)
                .values(**values_to_update)
                .returning(self._model)
            )
            result = await self._session.execute(stmt)
            await self._session.flush()
            await self._session.commit()  # добавлено commit
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(
                f"Ошибка обновления {self._model.__name__} с id {instance_id}: {e!s}"
            ) from e

    async def delete(self, instance_id: UUID) -> bool:
        """
        Удаляет запись по идентификатору.
        
        Args:
            instance_id: UUID идентификатор записи
            
        Returns:
            True если удаление успешно, иначе False
        """
        try:
            stmt = delete(self._model).where(self._model.id == instance_id)
            result = await self._session.execute(stmt)
            await self._session.flush()
            await self._session.commit()  # добавлено commit
            return (result.rowcount or 0) > 0  # изменено
        except Exception as e:
            raise Exception(
                f"Ошибка удаления {self._model.__name__} с id {instance_id}: {e!s}"
            ) from e

    async def exists(self, instance_id: UUID) -> bool:
        """
        Проверяет существование записи.
        
        Args:
            instance_id: UUID идентификатор записи
            
        Returns:
            True если запись существует, иначе False
        """
        query = select(exists().where(self._model.id == instance_id))
        result = await self._session.execute(query)
        return bool(result.scalar())  # изменено

    def __await__(self) -> Generator[Any, None, BaseRepository[ModelType]]:  # изменено
        # Позволяет ожидать экземпляр репозитория, возвращая self
        yield from ()
        return self
