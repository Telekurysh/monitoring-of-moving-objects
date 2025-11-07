from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Body
from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum

from src.sensor_track_pro.business_logic.models.user_model import UserBase
from src.sensor_track_pro.business_logic.models.user_model import UserModel
from src.sensor_track_pro.business_logic.services.user_service import UserService
from src.sensor_track_pro.data_access.database import get_async_db
from src.sensor_track_pro.data_access.repositories.users_repo import UserRepository


router = APIRouter()

_db_dep = Depends(get_async_db)


def get_user_service(session: AsyncSession = _db_dep) -> UserService:
    return UserService(UserRepository(session))


_user_service_dep = Depends(get_user_service)


@router.post("/", response_model=UserModel)
async def create_user(
    user_data: UserBase,
    password: str,
    service: UserService = _user_service_dep
) -> UserModel:
    return await service.create_user(user_data, password)


@router.get("/{user_id}", response_model=UserModel)
async def get_user(
    user_id: UUID,
    service: UserService = _user_service_dep
) -> UserModel:
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[UserModel])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    service: UserService = _user_service_dep
) -> list[UserModel]:
    return await service.get_users(skip=skip, limit=limit)


@router.put("/{user_id}", response_model=UserModel)
async def update_user(
    user_id: UUID,
    user_data: UserBase = Body(..., example={
        "email": "user@example.com",
        "username": "test",
        "is_active": True,
        "role": "admin"
    }),
    service: UserService = _user_service_dep
) -> UserModel:
    user = await service.update_user(user_id, user_data.dict())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=HTTP_204_NO_CONTENT, responses={404: {"description": "User not found"}})
async def delete_user(
    user_id: UUID,
    service: UserService = _user_service_dep
) -> Response:
    if not await service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=HTTP_204_NO_CONTENT)


# @router.post("/{user_id}/change-password")
# async def change_password(
#     user_id: UUID,
#     new_password: str,
#     service: UserService = _user_service_dep
# ) -> dict[str, str]:
#     if not await service.change_password(user_id, new_password):
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"status": "success"}


class UserAction(str, Enum):
    activate = "activate"
    deactivate = "deactivate"


@router.patch("/{user_id}/status")
async def set_user_status(
    user_id: UUID,
    action: UserAction = Query(..., description="'activate' or 'deactivate'"),
    service: UserService = _user_service_dep
) -> dict[str, str]:
    if action == UserAction.activate:
        ok = await service.activate_user(user_id)
    else:
        ok = await service.deactivate_user(user_id)

    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success"}
