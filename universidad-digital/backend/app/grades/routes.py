"""Grades CRUD with service-layer authorization."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.core.database import get_db
from app.grades import services
from app.grades.schemas import GradeCreate, GradeResponse, GradeUpdate
from app.users.models import User


router = APIRouter(prefix="/grades", tags=["grades"])


@router.post("", response_model=GradeResponse, status_code=201)
def create(
    data: GradeCreate, db: Session = Depends(get_db), actor: User = Depends(current_user)
) -> GradeResponse:
    return services.create_grade(db, data, actor)


@router.get("", response_model=list[GradeResponse])
def list_all(
    offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db), actor: User = Depends(current_user),
) -> list[GradeResponse]:
    return services.list_grades(db, actor, offset, limit)


@router.get("/{grade_id}", response_model=GradeResponse)
def get_one(
    grade_id: int, db: Session = Depends(get_db), actor: User = Depends(current_user)
) -> GradeResponse:
    return services.get_grade(db, grade_id, actor)


@router.put("/{grade_id}", response_model=GradeResponse)
def update(
    grade_id: int, data: GradeUpdate,
    db: Session = Depends(get_db), actor: User = Depends(current_user),
) -> GradeResponse:
    return services.update_grade(db, grade_id, data, actor)


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    grade_id: int, db: Session = Depends(get_db), actor: User = Depends(current_user)
) -> None:
    services.delete_grade(db, grade_id, actor)
