from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Body
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from starlette.status import HTTP_204_NO_CONTENT

from src.sensor_track_pro.business_logic.models.event_model import EventBase
from src.sensor_track_pro.business_logic.models.event_model import EventModel
from src.sensor_track_pro.business_logic.services.event_service import EventService
from src.sensor_track_pro.data_access.database import get_async_db
from src.sensor_track_pro.data_access.repositories.events_repo import EventRepository
from pydantic import BaseModel


class EventsResponse(BaseModel):
    items: list[EventModel]
    total: int | None = None


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



@router.get("/{event_id}", response_model=EventModel)
async def get_event(
    event_id: UUID,
    service: EventService = _event_service_dep
) -> EventModel:
    event = await service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/", response_model=EventsResponse)
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    # параметры для объединённых фильтров
    start_time: Optional[str] = Query(None, description="Start time in ISO format"),
    end_time: Optional[str] = Query(None, description="End time in ISO format"),
    sensor_id: UUID | None = Query(None),
    latitude: float | None = Query(None),
    longitude: float | None = Query(None),
    radius: float | None = Query(None),
    service: EventService = _event_service_dep
    ) -> EventsResponse:
    """
    Получить события. Поддерживаются фильтры (в порядке приоритета):
    - timerange (start_time & end_time)
    - sensor_id
    - coordinates (latitude, longitude, radius)
    Иначе возвращается общий список с пагинацией.
    Возвращает объект {items: [...], total: n}
    """
    # timerange
    if start_time is not None or end_time is not None:
        try:
            start_dt = datetime.fromisoformat(start_time) if start_time is not None else None
            end_dt = datetime.fromisoformat(end_time) if end_time is not None else None
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format.")
        items = await service.get_events_by_timerange(start_dt, end_dt)
        return EventsResponse(items=items, total=len(items))

    if sensor_id is not None:
        items = await service.get_events_by_sensor(sensor_id)
        return EventsResponse(items=items, total=len(items))

    if latitude is not None and longitude is not None and radius is not None:
        items = await service.get_events_by_coordinates(latitude, longitude, radius)
        return EventsResponse(items=items, total=len(items))

    items = await service.get_events(skip=skip, limit=limit)
    return EventsResponse(items=items, total=len(items))


@router.put("/{event_id}", response_model=EventModel)
async def update_event(
    event_id: UUID,
    event_data: EventBase = Body(..., example={
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "sensor_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "timestamp": "2025-10-11T09:57:06.684Z",
        "latitude": 0,
        "longitude": 0,
        "speed": 0,
        "event_type": "move",
        "details": "string",
    }),
    service: EventService = _event_service_dep
) -> EventModel:
    event = await service.update_event(event_id, event_data)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/{event_id}", status_code=HTTP_204_NO_CONTENT, responses={404: {"description": "Alert not found"}})
async def delete_event(
    event_id: UUID,
    service: EventService = _event_service_dep
) -> Response:
    if not await service.delete_event(event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return Response(status_code=HTTP_204_NO_CONTENT)
