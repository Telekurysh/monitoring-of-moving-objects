from __future__ import annotations

from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.interfaces.repository.iuser_model import IUserRepository
from src.sensor_track_pro.business_logic.models.common_types import FilterParams
from src.sensor_track_pro.business_logic.models.user_model import UserAuthData
from src.sensor_track_pro.business_logic.models.user_model import UserBase
from src.sensor_track_pro.business_logic.models.user_model import UserModel
from src.sensor_track_pro.business_logic.services.base_service import BaseService


class UserService(BaseService[UserModel]):
    def __init__(self, user_repository: IUserRepository):
        super().__init__(user_repository)
        self._user_repository = user_repository

    async def create_user(self, user_data: UserBase, password: str) -> UserModel:
        return await self._user_repository.create(user_data, password)

    async def authenticate_user(self, auth_data: UserAuthData) -> UserModel | None:
        return await self._user_repository.authenticate(auth_data)

    async def get_user(self, user_id: UUID) -> UserModel | None:
        return await self._user_repository.get_by_id(user_id)

    async def get_users(self, skip: int = 0, limit: int = 100, **filters: FilterParams) -> list[UserModel]:
        return await self._user_repository.get_all(skip, limit, **filters)

    async def update_user(self, user_id: UUID, user_data: dict[str, Any]) -> UserModel | None:
        return await self._user_repository.update(user_id, user_data)

    async def delete_user(self, user_id: UUID) -> bool:
        return await self._user_repository.delete(user_id)

    async def change_password(self, user_id: UUID, new_password: str) -> bool:
        return await self._user_repository.change_password(user_id, new_password)

    async def activate_user(self, user_id: UUID) -> bool:
        """Активирует учетную запись пользователя."""
        return await self._user_repository.activate_user(user_id)

    async def deactivate_user(self, user_id: UUID) -> bool:
        """Деактивирует учетную запись пользователя."""
        return await self._user_repository.deactivate_user(user_id)
