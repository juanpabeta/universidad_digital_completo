"""Report contract with numeric aggregates."""

from decimal import Decimal

from pydantic import BaseModel


class SubjectReport(BaseModel):
    id_materia: int
    materia: str
    inscripciones_activas: int
    promedio_calificaciones: Decimal | None
