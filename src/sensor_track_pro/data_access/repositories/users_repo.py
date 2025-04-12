from __future__ import annotations

import hashlib

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

    async def create(self, user_data: UserBase, password: str) -> UserModel:
        """Создает нового пользователя."""
        db_user = User(
            **user_data.model_dump(),
            password_hash=self._hash_password(password)
        )
        try:
            await super().create(db_user)
            return UserModel.model_validate(db_user)
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

    def _hash_password(self, password: str) -> str:
        """Хеширует пароль с использованием SHA-256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль, сравнивая SHA-256 хеш."""
        return self._hash_password(plain_password) == hashed_password
