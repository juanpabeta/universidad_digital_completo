"""Enrollment request and response."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EnrollmentCreate(BaseModel):
    id_usuario: int | None = Field(default=None, gt=0)
    id_materia: int = Field(gt=0)
    id_periodo: int = Field(gt=0)


class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_inscripcion: int
    id_usuario: int
    id_materia: int
    id_periodo: int
    fecha_inscripcion: datetime
    estado: Literal["ACTIVA", "CANCELADA"]
