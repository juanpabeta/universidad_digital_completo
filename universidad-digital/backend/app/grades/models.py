"""Multiple grades per enrollment with database-level bounds."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Grade(Base):
    __tablename__ = "calificaciones"
    __table_args__ = (
        CheckConstraint("nota >= 0 AND nota <= 100", name="ck_calificaciones_nota"),
        CheckConstraint(
            "tipo IN ('PARCIAL','FINAL','RECUPERACION')", name="ck_calificaciones_tipo"
        ),
    )

    id_calificacion: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_inscripcion: Mapped[int] = mapped_column(
        ForeignKey("inscripciones.id_inscripcion"), nullable=False
    )
    nota: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
