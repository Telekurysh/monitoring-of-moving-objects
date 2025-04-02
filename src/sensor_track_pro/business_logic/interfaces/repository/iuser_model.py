from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from uuid import UUID

from src.sensor_track_pro.business_logic.models.user_model import UserAuthData
from src.sensor_track_pro.business_logic.models.user_model import UserBase
from src.sensor_track_pro.business_logic.models.user_model import UserModel


class IUserRepository(ABC):
    """Интерфейс репозитория для работы с пользователями."""

    @abstractmethod
    async def create(self, user_data: UserBase, password: str) -> UserModel:
        """
        Создает нового пользователя.
        
        Args:
            user_data: Базовые данные пользователя
            password: Пароль для хеширования
            
        Returns:
            Созданный пользователь с хешем пароля
        """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserModel | None:
        """
        Получает пользователя по UUID.
        
        Args:
            user_id: Уникальный идентификатор пользователя
            
        Returns:
            Пользователь или None
        """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserModel | None:
        """
        Получает пользователя по имени пользователя.
        
        Args:
            username: Уникальное имя пользователя
            
        Returns:
            Пользователь или None
        """

    @abstractmethod
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            **filters: dict[str, Any]
    ) -> list[UserModel]:
        """
        Получает список пользователей с фильтрацией.
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            filters: Фильтры (role, is_active, email)
            
        Returns:
            Список пользователей
        """

    @abstractmethod
    async def update(
            self,
            user_id: UUID,
            user_data: dict[str, Any]
    ) -> UserModel | None:
        """
        Обновляет данные пользователя.
        
        Args:
            user_id: UUID пользователя
            user_data: Данные для частичного обновления
            
        Returns:
            Обновленный пользователь или None
        """

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Деактивирует пользователя (мягкое удаление).
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            Статус операции
        """

    @abstractmethod
    async def authenticate(self, auth_data: UserAuthData) -> UserModel | None:
        """
        Аутентификация пользователя.
        
        Args:
            auth_data: Данные для аутентификации
            
        Returns:
            Пользователь с валидными данными или None
        """

    @abstractmethod
    async def change_password(
            self,
            user_id: UUID,
            new_password: str
    ) -> bool:
        """
        Смена пароля пользователя.
        
        Args:
            user_id: UUID пользователя
            new_password: Новый пароль
            
        Returns:
            Статус операции
        """

    @abstractmethod
    async def activate_user(self, user_id: UUID) -> bool:
        """
        Активирует учетную запись пользователя.
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            Статус операции
        """

    @abstractmethod
    async def deactivate_user(self, user_id: UUID) -> bool:
        """
        Деактивирует учетную запись пользователя.
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            Статус операции
        """
