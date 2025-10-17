from __future__ import annotations

from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def error_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Resource already exists"}
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)}
    )
