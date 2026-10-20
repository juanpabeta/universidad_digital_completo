"""Grade authorization against assigned teacher and enrollment state."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import conflict, forbidden, not_found
from app.enrollments.models import Enrollment
from app.grades.models import Grade
from app.grades.schemas import GradeCreate, GradeUpdate
from app.subjects.models import Subject
from app.users.models import User


def _can_write(db: Session, actor: User, enrollment: Enrollment) -> bool:
    if any(role.nombre == "ADMINISTRADOR" for role in actor.roles):
        return True
    subject = db.get(Subject, enrollment.id_materia)
    return bool(
        subject and subject.id_docente == actor.id_usuario
        and any(role.nombre == "DOCENTE" for role in actor.roles)
    )


def _enrollment(db: Session, enrollment_id: int) -> Enrollment:
    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment is None:
        raise not_found("Inscripción")
    return enrollment


def get_grade(db: Session, grade_id: int, actor: User) -> Grade:
    grade = db.get(Grade, grade_id)
    if grade is None:
        raise not_found("Calificación")
    enrollment = _enrollment(db, grade.id_inscripcion)
    if enrollment.id_usuario != actor.id_usuario and not _can_write(db, actor, enrollment):
        raise forbidden()
    return grade


def list_grades(db: Session, actor: User, offset: int, limit: int) -> list[Grade]:
    stmt = select(Grade).join(Enrollment).order_by(Grade.id_calificacion)
    if not any(role.nombre == "ADMINISTRADOR" for role in actor.roles):
        if any(role.nombre == "DOCENTE" for role in actor.roles):
            stmt = stmt.join(Subject, Subject.id_materia == Enrollment.id_materia).where(
                Subject.id_docente == actor.id_usuario
            )
        else:
            stmt = stmt.where(Enrollment.id_usuario == actor.id_usuario)
    return list(db.scalars(stmt.offset(offset).limit(limit)))


def create_grade(db: Session, data: GradeCreate, actor: User) -> Grade:
    enrollment = _enrollment(db, data.id_inscripcion)
    if not _can_write(db, actor, enrollment):
        raise forbidden()
    if enrollment.estado != "ACTIVA":
        raise conflict("No se califica una inscripción cancelada")
    grade = Grade(**data.model_dump())
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


def update_grade(db: Session, grade_id: int, data: GradeUpdate, actor: User) -> Grade:
    grade = get_grade(db, grade_id, actor)
    enrollment = _enrollment(db, grade.id_inscripcion)
    if not _can_write(db, actor, enrollment):
        raise forbidden()
    if enrollment.estado != "ACTIVA":
        raise conflict("No se modifica una inscripción cancelada")
    grade.nota = data.nota
    grade.tipo = data.tipo
    db.commit()
    db.refresh(grade)
    return grade


def delete_grade(db: Session, grade_id: int, actor: User) -> None:
    if not any(role.nombre == "ADMINISTRADOR" for role in actor.roles):
        raise forbidden()
    grade = get_grade(db, grade_id, actor)
    db.delete(grade)
    db.commit()
