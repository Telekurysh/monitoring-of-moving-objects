from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.models.object_model import ObjectBase
from src.sensor_track_pro.business_logic.models.object_model import ObjectModel
from src.sensor_track_pro.business_logic.models.object_model import ObjectType
from src.sensor_track_pro.business_logic.services.object_service import ObjectService
from src.sensor_track_pro.data_access.database import get_async_db
from src.sensor_track_pro.data_access.repositories.objects_repo import ObjectRepository


router = APIRouter()

_db_dep = Depends(get_async_db)


def get_object_service(session: AsyncSession = _db_dep) -> ObjectService:
    return ObjectService(ObjectRepository(session))


_object_service_dep = Depends(get_object_service)


@router.post("/", response_model=ObjectBase)
async def create_object(
    object_data: ObjectBase,
    service: ObjectService = _object_service_dep
) -> ObjectBase:
    return await service.create_object(object_data)


@router.get("/{object_id}", response_model=ObjectModel)
async def get_object(
    object_id: UUID,
    service: ObjectService = _object_service_dep
) -> ObjectModel:
    obj = await service.get_object(object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj


@router.get("/", response_model=list[ObjectModel])
async def get_objects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    service: ObjectService = _object_service_dep
) -> list[ObjectModel]:
    return await service.get_objects(skip=skip, limit=limit)


@router.put("/{object_id}", response_model=ObjectModel)
async def update_object(
    object_id: UUID,
    object_data: ObjectBase,  # изменён тип аргумента для соответствия ObjectService
    service: ObjectService = _object_service_dep
) -> ObjectModel:
    obj = await service.update_object(object_id, object_data)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj


@router.delete("/{object_id}")
async def delete_object(
    object_id: UUID,
    service: ObjectService = _object_service_dep
) -> dict[str, str]:
    if not await service.delete_object(object_id):
        raise HTTPException(status_code=404, detail="Object not found")
    return {"status": "success"}


@router.get("/type/{object_type}", response_model=list[ObjectModel])
async def get_objects_by_type(
    object_type: ObjectType,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    service: ObjectService = _object_service_dep
) -> list[ObjectModel]:
    return await service.get_objects_by_type(object_type, skip, limit)
