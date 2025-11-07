from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.models.user_model import UserAuthData
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


@router.post("/register", response_model=UserModel)
async def register_user(
    user_data: UserBase,
    password: str,
    service: UserService = _user_service_dep
) -> UserModel:
    try:
        return await service.create_user(user_data, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=UserModel)
async def login_user(
    auth_data: UserAuthData,
    service: UserService = _user_service_dep
) -> Any:
    user = await service.authenticate_user(auth_data)
    if not user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    return user