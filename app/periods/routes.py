"""Period endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user, require_roles
from app.core.database import get_db
from app.periods import services
from app.periods.schemas import PeriodCreate, PeriodResponse, PeriodUpdate
from app.users.models import User


router = APIRouter(prefix="/periods", tags=["periods"])
Admin = Depends(require_roles("ADMINISTRADOR"))


@router.get("", response_model=list[PeriodResponse])
def list_all(
    offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db), _user: User = Depends(current_user),
) -> list[PeriodResponse]:
    return services.list_periods(db, offset, limit)


@router.get("/{period_id}", response_model=PeriodResponse)
def get_one(
    period_id: int, db: Session = Depends(get_db), _user: User = Depends(current_user)
) -> PeriodResponse:
    return services.get_period(db, period_id)


@router.post("", response_model=PeriodResponse, status_code=201)
def create(
    data: PeriodCreate, db: Session = Depends(get_db), _admin: User = Admin
) -> PeriodResponse:
    return services.create_period(db, data)


@router.put("/{period_id}", response_model=PeriodResponse)
def update(
    period_id: int, data: PeriodUpdate, db: Session = Depends(get_db), _admin: User = Admin
) -> PeriodResponse:
    return services.update_period(db, period_id, data)
