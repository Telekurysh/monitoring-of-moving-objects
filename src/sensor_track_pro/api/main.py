from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

from src.sensor_track_pro.api.routers import alerts
from src.sensor_track_pro.api.routers import auth
from src.sensor_track_pro.api.routers import events
from src.sensor_track_pro.api.routers import objects
from src.sensor_track_pro.api.routers import routes
from src.sensor_track_pro.api.routers import sensors
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

# Получаем абсолютный путь к директории проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to SensorTrackPro API"}


@app.get("/interface", response_class=HTMLResponse)
async def interface(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})
