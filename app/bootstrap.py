"""Create fixed roles and the first admin from protected environment values."""

import os

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.users.models import Role, User


ROLES = {
    "ADMINISTRADOR": "Administración académica",
    "DOCENTE": "Gestión docente",
    "ESTUDIANTE": "Consulta e inscripción estudiantil",
}


def main() -> None:
    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD", "")
    if not email or len(password) < 12:
        raise SystemExit("Defina ADMIN_EMAIL y ADMIN_PASSWORD de al menos 12 caracteres")
    with SessionLocal.begin() as db:
        for name, description in ROLES.items():
            if db.scalar(select(Role).where(Role.nombre == name)) is None:
                db.add(Role(nombre=name, descripcion=description))
        db.flush()
        admin = db.scalar(select(User).where(User.email == email))
        if admin is None:
            admin_role = db.scalar(select(Role).where(Role.nombre == "ADMINISTRADOR"))
            db.add(
                User(
                    nombres="Administración",
                    apellidos="Inicial",
                    email=email,
                    password_hash=hash_password(password),
                    roles=[admin_role],
                )
            )
    print("Roles disponibles y administrador inicial verificado")


if __name__ == "__main__":
    main()
