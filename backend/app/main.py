"""ASGI entrypoint and router composition."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.routes import router as auth_router
from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import AppError, app_error_handler
from app.enrollments.routes import router as enrollments_router
from app.grades.routes import router as grades_router
from app.periods.routes import router as periods_router
from app.reports.routes import router as reports_router
from app.subjects.routes import router as subjects_router
from app.users.routes import router as users_router


app = FastAPI(title="Universidad Digital API", version="1.0.0")
app.add_exception_handler(AppError, app_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

for router in (
    auth_router, users_router, subjects_router, periods_router,
    enrollments_router, grades_router, reports_router,
):
    app.include_router(router, prefix="/api/v1")


@app.get("/health/live", tags=["health"])
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
def readiness(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"database": "ready"}
