"""Academic period with valid dates."""

from datetime import date

from sqlalchemy import CheckConstraint, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AcademicPeriod(Base):
    __tablename__ = "periodos_academicos"
    __table_args__ = (
        CheckConstraint("fecha_fin >= fecha_inicio", name="ck_periodos_fechas"),
        CheckConstraint("estado IN ('ABIERTO','CERRADO')", name="ck_periodos_estado"),
    )

    id_periodo: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(String(10), default="ABIERTO", nullable=False)
