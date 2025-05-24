"""Бизнес-модели для работы с пользователями."""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


class UserRole(StrEnum):
    """Роли пользователей в системе."""

    ADMIN = "admin"  # Администратор
    OPERATOR = "operator"  # Оператор
    ANALYST = "analyst"  # Аналитик


class UserBase(BaseModel):
    """Базовые поля пользователя."""

    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    role: UserRole = Field(..., description="Роль пользователя")
    is_active: bool = Field(default=True, description="Признак активного пользователя")


class UserModel(UserBase):
    """Полная модель пользователя."""

    id: UUID  # убран default_factory
    password_hash: str = Field(..., description="Хэш пароля пользователя")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Дата и время создания пользователя")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)


class TokenModel(BaseModel):
    """Модель для токена аутентификации."""

    access_token: str = Field(..., description="Токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")
    user: UserModel = Field(..., description="Данные пользователя")


class UserAuthData(BaseModel):
    """Модель для аутентификации пользователя."""

    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя")
