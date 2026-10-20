"""Academic-period validation."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PeriodCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=30)
    fecha_inicio: date
    fecha_fin: date
    estado: Literal["ABIERTO", "CERRADO"] = "ABIERTO"

    @model_validator(mode="after")
    def valid_dates(self) -> "PeriodCreate":
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor o igual a fecha_inicio")
        return self


class PeriodUpdate(PeriodCreate):
    pass


class PeriodResponse(PeriodCreate):
    model_config = ConfigDict(from_attributes=True)

    id_periodo: int
