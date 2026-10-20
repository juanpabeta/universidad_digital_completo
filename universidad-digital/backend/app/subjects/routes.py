"""Subject endpoints; persistence remains in services."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user, require_roles
from app.core.database import get_db
from app.subjects import services
from app.subjects.schemas import SubjectCreate, SubjectResponse, SubjectUpdate
from app.users.models import User


router = APIRouter(prefix="/subjects", tags=["subjects"])
Admin = Depends(require_roles("ADMINISTRADOR"))


@router.get("", response_model=list[SubjectResponse])
def list_all(
    offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db), _user: User = Depends(current_user),
) -> list[SubjectResponse]:
    return services.list_subjects(db, offset, limit)


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_one(
    subject_id: int, db: Session = Depends(get_db), _user: User = Depends(current_user)
) -> SubjectResponse:
    return services.get_subject(db, subject_id)


@router.post("", response_model=SubjectResponse, status_code=201)
def create(
    data: SubjectCreate, db: Session = Depends(get_db), _admin: User = Admin
) -> SubjectResponse:
    return services.create_subject(db, data)


@router.put("/{subject_id}", response_model=SubjectResponse)
def update(
    subject_id: int, data: SubjectUpdate, db: Session = Depends(get_db), _admin: User = Admin
) -> SubjectResponse:
    return services.update_subject(db, subject_id, data)


@router.delete("/{subject_id}", response_model=SubjectResponse)
def deactivate(
    subject_id: int, db: Session = Depends(get_db), _admin: User = Admin
) -> SubjectResponse:
    return services.deactivate_subject(db, subject_id)
