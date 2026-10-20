"""Period lifecycle and uniqueness."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import conflict, not_found
from app.periods.models import AcademicPeriod
from app.periods.schemas import PeriodCreate, PeriodUpdate


def get_period(db: Session, period_id: int) -> AcademicPeriod:
    period = db.get(AcademicPeriod, period_id)
    if period is None:
        raise not_found("Período")
    return period


def list_periods(db: Session, offset: int, limit: int) -> list[AcademicPeriod]:
    return list(db.scalars(select(AcademicPeriod).order_by(AcademicPeriod.id_periodo).offset(offset).limit(limit)))


def create_period(db: Session, data: PeriodCreate) -> AcademicPeriod:
    period = AcademicPeriod(**data.model_dump())
    db.add(period)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("El período ya existe o viola una restricción") from exc
    db.refresh(period)
    return period


def update_period(db: Session, period_id: int, data: PeriodUpdate) -> AcademicPeriod:
    period = get_period(db, period_id)
    for field, value in data.model_dump().items():
        setattr(period, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("El período ya existe o viola una restricción") from exc
    db.refresh(period)
    return period
