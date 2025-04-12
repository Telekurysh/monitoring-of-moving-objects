from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from src.sensor_track_pro.data_access.models.base import Base


class UserObject(Base):
    """Модель связи пользователя с объектом."""

    user_id = Column(String(36), ForeignKey("user.id"), primary_key=True)
    object_id = Column(String(36), ForeignKey("object.id"), primary_key=True)
    access_level = Column(String(50), nullable=False)

    # Связи
    user = relationship("User")
    object = relationship("Object")

    __table_args__ = (
        UniqueConstraint("user_id", "object_id"),
    )