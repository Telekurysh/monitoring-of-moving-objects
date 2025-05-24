from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.sensor_track_pro.business_logic.models.event_model import EventBase
from src.sensor_track_pro.business_logic.models.event_model import EventModel
from src.sensor_track_pro.business_logic.services.event_service import EventService
from src.sensor_track_pro.data_access.database import get_async_db
from src.sensor_track_pro.data_access.repositories.events_repo import EventRepository


_db_dep = Depends(get_async_db)

router = APIRouter()


def get_event_service(session: AsyncSession = _db_dep) -> EventService:
    return EventService(EventRepository(session))


_event_service_dep = Depends(get_event_service)


@router.post("/", response_model=EventModel)
async def create_event(
    event_data: EventBase,
    service: EventService = _event_service_dep
) -> EventModel:
    return await service.create_event(event_data)


@router.get("/timerange", response_model=list[EventModel])
async def get_events_by_timerange(
    start_time: str,
    end_time: str,
    service: EventService = _event_service_dep
) -> list[EventModel]:
    # Преобразуем строки к datetime
    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format.")
    return await service.get_events_by_timerange(start_dt, end_dt)


@router.get("/{event_id}", response_model=EventModel)
async def get_event(
    event_id: UUID,
    service: EventService = _event_service_dep
) -> EventModel:
    event = await service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/", response_model=list[EventModel])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    service: EventService = _event_service_dep
) -> list[EventModel]:
    return await service.get_events(skip=skip, limit=limit)


@router.put("/{event_id}", response_model=EventModel)
async def update_event(
    event_id: UUID,
    event_data: dict[str, Any],
    service: EventService = _event_service_dep
) -> EventModel:
    event = await service.update_event(event_id, event_data)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: UUID,
    service: EventService = _event_service_dep
) -> dict[str, Any]:
    if not await service.delete_event(event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return {"status": "success"}


@router.get("/sensor/{sensor_id}", response_model=list[EventModel])
async def get_events_by_sensor(
    sensor_id: UUID,
    service: EventService = _event_service_dep
) -> list[EventModel]:
    return await service.get_events_by_sensor(sensor_id)


@router.get("/coordinates", response_model=list[EventModel])
async def get_events_by_coordinates(
    latitude: float,
    longitude: float,
    radius: float,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    service: EventService = _event_service_dep
) -> list[EventModel]:
    return await service.get_events_by_coordinates(latitude, longitude, radius)
