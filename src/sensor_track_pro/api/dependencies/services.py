from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.services.alert_service import AlertService
from src.sensor_track_pro.business_logic.services.event_service import EventService
from src.sensor_track_pro.business_logic.services.object_service import ObjectService
from src.sensor_track_pro.business_logic.services.route_service import RouteService
from src.sensor_track_pro.business_logic.services.sensor_service import SensorService
from src.sensor_track_pro.business_logic.services.user_service import UserService
from src.sensor_track_pro.business_logic.services.zone_service import ZoneService
from src.sensor_track_pro.data_access.database import get_async_db
from src.sensor_track_pro.data_access.repositories.alerts_repo import AlertRepository
from src.sensor_track_pro.data_access.repositories.events_repo import EventRepository
from src.sensor_track_pro.data_access.repositories.objects_repo import ObjectRepository
from src.sensor_track_pro.data_access.repositories.routes_repo import RouteRepository
from src.sensor_track_pro.data_access.repositories.sensors_repo import SensorRepository
from src.sensor_track_pro.data_access.repositories.users_repo import UserRepository
from src.sensor_track_pro.data_access.repositories.zones_repo import ZoneRepository


db_dep = Depends(get_async_db)


def get_user_service(session: AsyncSession = db_dep) -> UserService:
    return UserService(UserRepository(session))


def get_zone_service(session: AsyncSession = db_dep) -> ZoneService:
    return ZoneService(ZoneRepository(session))


def get_sensor_service(session: AsyncSession = db_dep) -> SensorService:
    return SensorService(SensorRepository(session))


def get_route_service(session: AsyncSession = db_dep) -> RouteService:
    return RouteService(RouteRepository(session))


def get_object_service(session: AsyncSession = db_dep) -> ObjectService:
    return ObjectService(ObjectRepository(session))


def get_event_service(session: AsyncSession = db_dep) -> EventService:
    return EventService(EventRepository(session))


def get_alert_service(session: AsyncSession = db_dep) -> AlertService:
    return AlertService(AlertRepository(session))
