"""Subject lifecycle and teacher-role rule."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import conflict, not_found
from app.subjects.models import Subject
from app.subjects.schemas import SubjectCreate, SubjectUpdate
from app.users.models import User


def _validate_teacher(db: Session, teacher_id: int | None) -> None:
    if teacher_id is None:
        return
    teacher = db.get(User, teacher_id)
    if teacher is None or not teacher.activo or not any(
        role.nombre == "DOCENTE" for role in teacher.roles
    ):
        raise conflict("El docente asignado debe existir, estar activo y tener rol DOCENTE")


def get_subject(db: Session, subject_id: int) -> Subject:
    subject = db.get(Subject, subject_id)
    if subject is None:
        raise not_found("Materia")
    return subject


def list_subjects(db: Session, offset: int, limit: int) -> list[Subject]:
    return list(db.scalars(select(Subject).order_by(Subject.id_materia).offset(offset).limit(limit)))


def create_subject(db: Session, data: SubjectCreate) -> Subject:
    _validate_teacher(db, data.id_docente)
    subject = Subject(**data.model_dump())
    db.add(subject)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("El código de materia ya existe") from exc
    db.refresh(subject)
    return subject


def update_subject(db: Session, subject_id: int, data: SubjectUpdate) -> Subject:
    subject = get_subject(db, subject_id)
    _validate_teacher(db, data.id_docente)
    for field, value in data.model_dump().items():
        setattr(subject, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("El código de materia ya existe") from exc
    db.refresh(subject)
    return subject


def deactivate_subject(db: Session, subject_id: int) -> Subject:
    subject = get_subject(db, subject_id)
    subject.activa = False
    db.commit()
    db.refresh(subject)
    return subject
