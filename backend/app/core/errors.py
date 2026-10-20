"""Domain errors and a consistent, non-sensitive HTTP representation."""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def not_found(resource: str) -> AppError:
    return AppError(404, "not_found", f"{resource} no encontrado")


def conflict(message: str) -> AppError:
    return AppError(409, "conflict", message)


def forbidden() -> AppError:
    return AppError(403, "forbidden", "No tiene permiso para esta operación")
