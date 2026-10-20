"""Aggregate enrollment and grade data without multiplying counts."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import forbidden, not_found
from app.enrollments.models import Enrollment
from app.grades.models import Grade
from app.periods.models import AcademicPeriod
from app.reports.schemas import SubjectReport
from app.subjects.models import Subject
from app.users.models import User


def by_period(db: Session, period_id: int, actor: User) -> list[SubjectReport]:
    if not any(role.nombre in {"ADMINISTRADOR", "DOCENTE"} for role in actor.roles):
        raise forbidden()
    if db.get(AcademicPeriod, period_id) is None:
        raise not_found("Período")
    enrollments = (
        select(
            Enrollment.id_materia.label("subject_id"),
            func.count(Enrollment.id_inscripcion).label("total"),
        )
        .where(Enrollment.id_periodo == period_id, Enrollment.estado == "ACTIVA")
        .group_by(Enrollment.id_materia)
        .subquery()
    )
    grades = (
        select(
            Enrollment.id_materia.label("subject_id"),
            func.avg(Grade.nota).label("average"),
        )
        .join(Grade, Grade.id_inscripcion == Enrollment.id_inscripcion)
        .where(Enrollment.id_periodo == period_id, Enrollment.estado == "ACTIVA")
        .group_by(Enrollment.id_materia)
        .subquery()
    )
    query = (
        select(
            Subject.id_materia,
            Subject.nombre,
            func.coalesce(enrollments.c.total, 0),
            grades.c.average,
        )
        .outerjoin(enrollments, enrollments.c.subject_id == Subject.id_materia)
        .outerjoin(grades, grades.c.subject_id == Subject.id_materia)
        .order_by(Subject.id_materia)
    )
    if not any(role.nombre == "ADMINISTRADOR" for role in actor.roles):
        query = query.where(Subject.id_docente == actor.id_usuario)
    return [
        SubjectReport(
            id_materia=subject_id,
            materia=name,
            inscripciones_activas=count,
            promedio_calificaciones=average,
        )
        for subject_id, name, count, average in db.execute(query)
    ]
