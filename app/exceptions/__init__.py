from fastapi import Request
from fastapi.responses import JSONResponse

from .base import AppException
from .http import (
    EntityNotFound,
    EntityAlreadyExists,
    InvalidOperation,
    ValidationError,
    DatabaseError,
)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


__all__ = [
    "AppException",
    "EntityNotFound",
    "EntityAlreadyExists",
    "InvalidOperation",
    "ValidationError",
    "DatabaseError",
    "app_exception_handler",
]

