from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.sensor_track_pro.api.routers import alerts
from src.sensor_track_pro.api.routers import auth
from src.sensor_track_pro.api.routers import events
from src.sensor_track_pro.api.routers import objects
from src.sensor_track_pro.api.routers import routes
from src.sensor_track_pro.api.routers import sensors
from src.sensor_track_pro.api.routers import telemetry
from src.sensor_track_pro.api.routers import users
from src.sensor_track_pro.api.routers import zones


app = FastAPI(
    title="SensorTrackPro API",
    description="API для системы мониторинга объектов",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(zones.router, prefix="/api/zones", tags=["zones"])
app.include_router(sensors.router, prefix="/api/sensors", tags=["sensors"])
app.include_router(routes.router, prefix="/api/routes", tags=["routes"])
app.include_router(objects.router, prefix="/api/objects", tags=["objects"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to SensorTrackPro API"}
