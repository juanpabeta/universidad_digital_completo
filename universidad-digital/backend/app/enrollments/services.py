"""Enrollment rules, visibility and cancellation."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import conflict, forbidden, not_found
from app.enrollments.models import Enrollment
from app.enrollments.schemas import EnrollmentCreate
from app.periods.models import AcademicPeriod
from app.subjects.models import Subject
from app.users.models import User


def _has_role(user: User, name: str) -> bool:
    return any(role.nombre == name for role in user.roles)


def get_enrollment(db: Session, enrollment_id: int, actor: User) -> Enrollment:
    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment is None:
        raise not_found("Inscripción")
    if _has_role(actor, "ADMINISTRADOR") or enrollment.id_usuario == actor.id_usuario:
        return enrollment
    subject = db.get(Subject, enrollment.id_materia)
    if _has_role(actor, "DOCENTE") and subject and subject.id_docente == actor.id_usuario:
        return enrollment
    raise forbidden()


def list_enrollments(db: Session, actor: User, offset: int, limit: int) -> list[Enrollment]:
    stmt = select(Enrollment).order_by(Enrollment.id_inscripcion)
    if not _has_role(actor, "ADMINISTRADOR"):
        if _has_role(actor, "DOCENTE"):
            stmt = stmt.join(Subject, Subject.id_materia == Enrollment.id_materia).where(
                Subject.id_docente == actor.id_usuario
            )
        else:
            stmt = stmt.where(Enrollment.id_usuario == actor.id_usuario)
    return list(db.scalars(stmt.offset(offset).limit(limit)))


def create_enrollment(db: Session, data: EnrollmentCreate, actor: User) -> Enrollment:
    admin = _has_role(actor, "ADMINISTRADOR")
    if not admin and not _has_role(actor, "ESTUDIANTE"):
        raise forbidden()
    student_id = data.id_usuario if admin and data.id_usuario else actor.id_usuario
    if not admin and data.id_usuario not in (None, actor.id_usuario):
        raise forbidden()
    student = db.get(User, student_id)
    subject = db.get(Subject, data.id_materia)
    period = db.get(AcademicPeriod, data.id_periodo)
    if student is None or not student.activo or not _has_role(student, "ESTUDIANTE"):
        raise conflict("El estudiante debe existir, estar activo y tener rol ESTUDIANTE")
    if subject is None or not subject.activa:
        raise conflict("La materia no existe o está inactiva")
    today = date.today()
    if period is None or period.estado != "ABIERTO" or not (
        period.fecha_inicio <= today <= period.fecha_fin
    ):
        raise conflict("El período debe estar abierto y dentro de sus fechas")
    enrollment = Enrollment(
        id_usuario=student_id, id_materia=data.id_materia, id_periodo=data.id_periodo
    )
    db.add(enrollment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("El estudiante ya está inscrito en esa materia y período") from exc
    db.refresh(enrollment)
    return enrollment


def cancel_enrollment(db: Session, enrollment_id: int, actor: User) -> Enrollment:
    enrollment = get_enrollment(db, enrollment_id, actor)
    if not (_has_role(actor, "ADMINISTRADOR") or enrollment.id_usuario == actor.id_usuario):
        raise forbidden()
    if enrollment.estado == "CANCELADA":
        return enrollment
    enrollment.estado = "CANCELADA"
    db.commit()
    db.refresh(enrollment)
    return enrollment
