from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Body
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT

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
    object_type: ObjectType | None = Query(None),
    service: ObjectService = _object_service_dep
) -> list[ObjectModel]:
    if object_type is not None:
        return await service.get_objects_by_type(object_type, skip, limit)
    return await service.get_objects(skip=skip, limit=limit)


@router.put("/{object_id}", response_model=ObjectModel)
async def update_object(
    object_id: UUID,
    object_data: ObjectBase = Body(..., example={
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "string",
            "object_type": "vehicle",
            "description": "string",
        }),
    service: ObjectService = _object_service_dep
) -> ObjectModel:
    obj = await service.update_object(object_id, object_data)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj


@router.delete("/{object_id}", status_code=HTTP_204_NO_CONTENT, responses={404: {"description": "Alert not found"}})
async def delete_object(
    object_id: UUID,
    service: ObjectService = _object_service_dep
) -> Response:
    if not await service.delete_object(object_id):
        raise HTTPException(status_code=404, detail="Object not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


# old route /type/{object_type} consolidated into root GET / with query param


@router.get("/map/all", include_in_schema=False)
async def get_objects_for_map(
    service: ObjectService = _object_service_dep
) -> list[dict]:
    return await service.get_objects_for_map()
