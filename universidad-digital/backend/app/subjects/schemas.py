"""Validated subject input and output."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    codigo: str = Field(min_length=2, max_length=30)
    creditos: int = Field(ge=1, le=30)
    id_docente: int | None = Field(default=None, gt=0)

    @field_validator("codigo")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()


class SubjectUpdate(SubjectCreate):
    activa: bool


class SubjectResponse(SubjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id_materia: int
    activa: bool
