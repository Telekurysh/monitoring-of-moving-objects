from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.interfaces.repository.iobject_repo import IObjectRepository
from src.sensor_track_pro.business_logic.models.object_model import ObjectModel
from src.sensor_track_pro.business_logic.models.object_model import ObjectBase
from src.sensor_track_pro.business_logic.models.object_model import ObjectType
from src.sensor_track_pro.data_access.models.objects import Object
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class ObjectRepository(BaseRepository[Object], IObjectRepository):  # type: ignore[misc]
    """Репозиторий для работы с объектами."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Object)

    async def create(self, object_data: ObjectBase) -> ObjectModel:  # type: ignore[override]
        """Создает новый объект."""
        db_object_dict = object_data.model_dump(exclude={"id", "created_at", "updated_at"})
        if "object_type" in db_object_dict or "type" in db_object_dict:
            # Извлекаем значение из ключей object_type/type и присваиваем ключу object_type
            obj_type = db_object_dict.pop("object_type", None) or db_object_dict.pop("type", None)
            if hasattr(obj_type, "value"):
                db_object_dict["object_type"] = str(obj_type.value).lower()  # преобразование в нижний регистр
            else:
                db_object_dict["object_type"] = str(obj_type).lower()
        db_object = Object(**db_object_dict)
        created_instance = await super().create(db_object)
        return ObjectModel.model_validate(created_instance)

    async def get_by_type(
        self,
        object_type: ObjectType,
        skip: int = 0,
        limit: int = 100
    ) -> list[ObjectModel]:
        """Получает объекты определенного типа."""
        query = (
            select(Object)
            .filter(Object.object_type == object_type)  # изменено с type на object_type
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [ObjectModel.model_validate(obj) for obj in result.scalars().all()]

    async def get_count(self, **filters: Any) -> int:
        """Получает количество объектов с фильтрами."""
        query = select(Object)
        for field, value in filters.items():
            if hasattr(Object, field):
                query = query.filter(getattr(Object, field) == value)
        result = await self._session.execute(query)
        return len(result.scalars().all())
