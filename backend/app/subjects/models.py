"""Subject and assigned teacher."""

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Subject(Base):
    __tablename__ = "materias"
    __table_args__ = (CheckConstraint("creditos > 0", name="ck_materias_creditos"),)

    id_materia: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    creditos: Mapped[int] = mapped_column(Integer, nullable=False)
    activa: Mapped[bool] = mapped_column(default=True, nullable=False)
    id_docente: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="RESTRICT"), nullable=True
    )
