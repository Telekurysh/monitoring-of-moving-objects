from __future__ import annotations

from uuid import UUID

from src.sensor_track_pro.business_logic.interfaces.repository.iobject_repo import IObjectRepository
from src.sensor_track_pro.business_logic.models.common_types import FilterParams
from src.sensor_track_pro.business_logic.models.object_model import ObjectBase
from src.sensor_track_pro.business_logic.models.object_model import ObjectModel
from src.sensor_track_pro.business_logic.models.object_model import ObjectType
from src.sensor_track_pro.business_logic.services.base_service import BaseService


class ObjectService(BaseService[ObjectModel]):
    def __init__(self, object_repository: IObjectRepository):
        super().__init__(object_repository)
        self._object_repository = object_repository

    async def create_object(self, object_data: ObjectModel) -> ObjectModel:
        return await self._object_repository.create(object_data)

    async def get_object(self, object_id: UUID) -> ObjectModel | None:
        return await self._object_repository.get_by_id(object_id)

    async def get_objects(self, skip: int = 0, limit: int = 100, **filters: FilterParams) -> list[ObjectModel]:
        return await self._object_repository.get_all(skip, limit, **filters)

    async def update_object(self, object_id: UUID, object_data: ObjectBase) -> ObjectModel | None:
        return await self._object_repository.update(object_id, object_data)

    async def delete_object(self, object_id: UUID) -> bool:
        return await self._object_repository.delete(object_id)

    async def get_objects_by_type(self, object_type: ObjectType, skip: int = 0, limit: int = 100) -> list[ObjectModel]:
        return await self._object_repository.get_by_type(object_type, skip, limit)
