"""Grade values and allowed assessment types."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


GradeType = Literal["PARCIAL", "FINAL", "RECUPERACION"]


class GradeCreate(BaseModel):
    id_inscripcion: int = Field(gt=0)
    nota: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    tipo: GradeType


class GradeUpdate(BaseModel):
    nota: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    tipo: GradeType


class GradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_calificacion: int
    id_inscripcion: int
    nota: Decimal
    tipo: GradeType
    fecha_registro: datetime
