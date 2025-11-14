from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
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

# add instance header so responses indicate which container served the request
@app.middleware("http")
async def add_instance_header(request: Request, call_next):
    response = await call_next(request)
    try:
        import socket
        instance_name = os.environ.get("INSTANCE_NAME") or socket.gethostname()
        response.headers["X-Instance"] = instance_name
    except Exception:
        pass
    return response

# Handle database permission errors (e.g. write attempted on read-only user/replica)
try:
    import asyncpg
    _AsyncPGError = asyncpg.PostgresError
except Exception:
    _AsyncPGError = None


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # If this is a postgres permission error, return a friendly 'write to read-only' response
    msg = str(exc)
    if _AsyncPGError is not None and isinstance(exc, _AsyncPGError):
        lower = msg.lower()
        if "permission denied" in lower or "read-only" in lower or "insufficient" in lower:
            return JSONResponse(status_code=403, content={"detail": "Write attempted on read-only DB instance"})
        return JSONResponse(status_code=500, content={"detail": "Database error", "error": msg})

    # Fallback: if the message contains permission-related text, transform it
    lower = msg.lower()
    if "permission denied" in lower or "read-only" in lower or "insufficient" in lower:
        return JSONResponse(status_code=403, content={"detail": "Write attempted on read-only DB instance"})

    # otherwise propagate as 500
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

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
# Health endpoints for mounted sub-applications. These return 200 for
# <prefix>/health (used by proxies and healthchecks). When the mirror
# proxy preserves the prefix, /mirror/api/v1/health will reach this
# handler and return ok instead of 404.
@app_v1.get("/health", include_in_schema=False)
async def health_v1() -> dict[str, str]:
    return {"status": "ok"}

@app_v2.get("/health", include_in_schema=False)
async def health_v2() -> dict[str, str]:
    return {"status": "ok"}

app.mount(api_settings.api_v1_prefix, app_v1)
app.mount(api_settings.api_v2_prefix, app_v2)
