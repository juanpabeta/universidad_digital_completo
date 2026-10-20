"""Users, roles and the many-to-many association."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


user_role = Table(
    "usuario_rol",
    Base.metadata,
    Column("id_usuario", ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True),
    Column("id_rol", ForeignKey("roles.id_rol", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id_rol: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(150), nullable=False)


class User(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    roles: Mapped[list[Role]] = relationship(secondary=user_role, lazy="selectin")
