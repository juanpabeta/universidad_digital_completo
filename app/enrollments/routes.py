"""Authenticated enrollment API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.core.database import get_db
from app.enrollments import services
from app.enrollments.schemas import EnrollmentCreate, EnrollmentResponse
from app.users.models import User


router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.post("", response_model=EnrollmentResponse, status_code=201)
def create(
    data: EnrollmentCreate,
    db: Session = Depends(get_db), actor: User = Depends(current_user),
) -> EnrollmentResponse:
    return services.create_enrollment(db, data, actor)


@router.get("", response_model=list[EnrollmentResponse])
def list_all(
    offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db), actor: User = Depends(current_user),
) -> list[EnrollmentResponse]:
    return services.list_enrollments(db, actor, offset, limit)


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_one(
    enrollment_id: int,
    db: Session = Depends(get_db), actor: User = Depends(current_user),
) -> EnrollmentResponse:
    return services.get_enrollment(db, enrollment_id, actor)


@router.delete("/{enrollment_id}", response_model=EnrollmentResponse)
def cancel(
    enrollment_id: int,
    db: Session = Depends(get_db), actor: User = Depends(current_user),
) -> EnrollmentResponse:
    return services.cancel_enrollment(db, enrollment_id, actor)
