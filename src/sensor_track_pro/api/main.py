from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

# Импорты для v1
from src.sensor_track_pro.api.routers.v1 import alerts as alerts_v1
from src.sensor_track_pro.api.routers.v1 import auth as auth_v1
from src.sensor_track_pro.api.routers.v1 import events as events_v1
from src.sensor_track_pro.api.routers.v1 import objects as objects_v1
from src.sensor_track_pro.api.routers.v1 import routes as routes_v1
from src.sensor_track_pro.api.routers.v1 import sensors as sensors_v1
from src.sensor_track_pro.api.routers.v1 import users as users_v1
from src.sensor_track_pro.api.routers.v1 import zones as zones_v1

# Импорты для v2
from src.sensor_track_pro.api.routers.v2 import alerts as alerts_v2
from src.sensor_track_pro.api.routers.v2 import auth as auth_v2
from src.sensor_track_pro.api.routers.v2 import events as events_v2
from src.sensor_track_pro.api.routers.v2 import objects as objects_v2
from src.sensor_track_pro.api.routers.v2 import routes as routes_v2
from src.sensor_track_pro.api.routers.v2 import sensors as sensors_v2
from src.sensor_track_pro.api.routers.v2 import users as users_v2
from src.sensor_track_pro.api.routers.v2 import zones as zones_v2

from src.sensor_track_pro.api.config import api_settings

app = FastAPI(
    title=api_settings.project_name,
    description=f"API для системы мониторинга объектов (version {api_settings.version})",
    version=api_settings.version,
    docs_url=None,  # disable root docs to avoid collision with mounted apps
    redoc_url=None,
    openapi_url=None,
)

# Create sub-applications for v1 and v2 so each has its own documentation pages
app_v1 = FastAPI(
    title=f"{api_settings.project_name} API v1",
    description=f"API v1 для системы мониторинга объектов (version {api_settings.version})",
    version=api_settings.version,
    docs_url=f"/docs",
    redoc_url=f"/redoc",
    openapi_url=f"/openapi.json",
)

app_v2 = FastAPI(
    title=f"{api_settings.project_name} API v2",
    description=f"API v2 для системы мониторинга объектов (version {api_settings.version})",
    version=api_settings.version,
    docs_url=f"/docs",
    redoc_url=f"/redoc",
    openapi_url=f"/openapi.json",
)

# CORS middleware
# Apply CORS to root app so static/templates are accessible; sub-apps inherit middleware when mounted
app.add_middleware(
    CORSMiddleware,
    allow_origins=api_settings.allowed_origins,
    allow_credentials=True,
    allow_methods=api_settings.allowed_methods,
    allow_headers=api_settings.allowed_headers,
)

# Подключаем роутеры к под-приложениям
# v1 routers
app_v1.include_router(users_v1.router, prefix="/users", tags=["users-v1"])
app_v1.include_router(zones_v1.router, prefix="/zones", tags=["zones-v1"])
app_v1.include_router(sensors_v1.router, prefix="/sensors", tags=["sensors-v1"])
app_v1.include_router(routes_v1.router, prefix="/routes", tags=["routes-v1"])
app_v1.include_router(objects_v1.router, prefix="/objects", tags=["objects-v1"])
app_v1.include_router(events_v1.router, prefix="/events", tags=["events-v1"])
app_v1.include_router(alerts_v1.router, prefix="/alerts", tags=["alerts-v1"])

# v2 routers
app_v2.include_router(users_v2.router, prefix="/users", tags=["users-v2"])
app_v2.include_router(zones_v2.router, prefix="/zones", tags=["zones-v2"])
app_v2.include_router(sensors_v2.router, prefix="/sensors", tags=["sensors-v2"])
app_v2.include_router(routes_v2.router, prefix="/routes", tags=["routes-v2"])
app_v2.include_router(objects_v2.router, prefix="/objects", tags=["objects-v2"])
app_v2.include_router(events_v2.router, prefix="/events", tags=["events-v2"])
app_v2.include_router(alerts_v2.router, prefix="/alerts", tags=["alerts-v2"])


# Получаем абсолютный путь к директории проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"message": "Welcome to SensorTrackPro API"}


@app.get("/interface", response_class=HTMLResponse, include_in_schema=False)
async def interface(request: Request) -> HTMLResponse:
    # Передаём префикс API в шаблон, чтобы фронтенд использовал корректный путь (например, /api/v1)
    return templates.TemplateResponse("index.html", {"request": request, "api_prefix": api_settings.api_v1_prefix})


# Mount sub-applications so their docs are available at /api/v1/docs and /api/v2/docs
app.mount(api_settings.api_v1_prefix, app_v1)
app.mount(api_settings.api_v2_prefix, app_v2)
