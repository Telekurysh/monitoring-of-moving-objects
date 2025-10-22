from __future__ import annotations

import hashlib

from typing import Any  # добавлено
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.interfaces.repository.iuser_model import IUserRepository
from src.sensor_track_pro.business_logic.models.user_model import UserAuthData
from src.sensor_track_pro.business_logic.models.user_model import UserBase
from src.sensor_track_pro.business_logic.models.user_model import UserModel
from src.sensor_track_pro.data_access.models.users import User
from src.sensor_track_pro.data_access.repositories.base import BaseRepository


class UserRepository(BaseRepository[User], IUserRepository):
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def create(self, user_data: UserBase, password: str) -> UserModel:  # type: ignore[override]
        """Создает нового пользователя."""
        user_dict = user_data.model_dump(exclude_unset=True)
        # Удаляем id, created_at, updated_at если вдруг есть
        user_dict.pop("id", None)
        user_dict.pop("created_at", None)
        user_dict.pop("updated_at", None)
        # Приводим роль к строковому значению для Enum в БД (нижний регистр!)
        if "role" in user_dict:
            role = user_dict["role"]
            # Исправлено: всегда получаем строку значения Enum (или строку) и приводим к нижнему регистру
            if hasattr(role, "value"):
                user_dict["role"] = str(role.value).lower()
            else:
                user_dict["role"] = str(role).lower()
        db_user = User(
            **user_dict,
            password_hash=self._hash_password(password)
        )
        try:
            instance = await super().create(db_user)
            return UserModel.model_validate(instance)
        except IntegrityError:
            raise ValueError("Пользователь с таким именем уже существует")

    async def get_by_username(self, username: str) -> UserModel | None:
        """Получает пользователя по имени."""
        query = select(User).filter(User.username == username)
        result = await self._session.execute(query)
        db_user = result.scalar_one_or_none()
        return UserModel.model_validate(db_user) if db_user else None

    async def authenticate(self, auth_data: UserAuthData) -> UserModel | None:
        """Аутентифицирует пользователя."""
        db_user = await self.get_by_username(auth_data.username)
        if db_user and self._verify_password(
            auth_data.password,
            db_user.password_hash
        ):
            return db_user
        return None

    async def change_password(
        self,
        user_id: UUID,
        new_password: str
    ) -> bool:
        """Меняет пароль пользователя."""
        db_user = await super().get_by_id(user_id)
        if db_user:
            db_user.password_hash = self._hash_password(new_password)
            await self._session.flush()
            return True
        return False

    async def get_by_id(self, user_id: UUID) -> UserModel | None:  # type: ignore[override]
        """Получает пользователя по ID."""
        db_user = await super().get_by_id(user_id)
        return UserModel.model_validate(db_user) if db_user else None

    async def get_all(self, skip: int = 0, limit: int = 100, **filters: dict[str, Any]) -> list[UserModel]:  # type: ignore[override]
        """Получает всех пользователей с возможностью фильтрации."""
        db_users = await super().get_all(skip, limit, **filters)
        return [UserModel.model_validate(u) for u in db_users]

    async def update(self, user_id: UUID, user_data: dict[str, Any]) -> UserModel | None:  # type: ignore[override]
        """Обновляет данные пользователя."""
        # Приводим роль к строке в нижнем регистре, если есть
        if "role" in user_data:
            role = user_data["role"]
            if hasattr(role, "value"):
                user_data["role"] = str(role.value).lower()
            else:
                user_data["role"] = str(role).lower()
        db_user = await super().update(user_id, user_data)
        return UserModel.model_validate(db_user) if db_user else None

    # async def delete(self, user_id: UUID) -> bool:
    #     """Удаляет пользователя."""
    #     return await super().delete(user_id)
    
    async def activate_user(self, user_id: UUID) -> bool:
        updated_user = await self.update(user_id, {"is_active": True})
        return updated_user is not None

    async def deactivate_user(self, user_id: UUID) -> bool:
        updated_user = await self.update(user_id, {"is_active": False})
        return updated_user is not None

    def _hash_password(self, password: str) -> str:
        """Хеширует пароль с использованием SHA-256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль, сравнивая SHA-256 хеш."""
        return self._hash_password(plain_password) == hashed_password
