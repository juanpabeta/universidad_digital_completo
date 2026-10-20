"""Enrollment references student, subject and academic period."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Enrollment(Base):
    __tablename__ = "inscripciones"
    __table_args__ = (
        UniqueConstraint("id_usuario", "id_materia", "id_periodo", name="uq_inscripcion_unica"),
        CheckConstraint("estado IN ('ACTIVA','CANCELADA')", name="ck_inscripcion_estado"),
    )

    id_inscripcion: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)
    id_materia: Mapped[int] = mapped_column(ForeignKey("materias.id_materia"), nullable=False)
    id_periodo: Mapped[int] = mapped_column(ForeignKey("periodos_academicos.id_periodo"), nullable=False)
    fecha_inscripcion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    estado: Mapped[str] = mapped_column(default="ACTIVA", nullable=False)
