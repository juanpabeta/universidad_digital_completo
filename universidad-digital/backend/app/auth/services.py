"""Password verification and token issuance."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import create_access_token, verify_password
from app.users.models import User


def login(db: Session, email: str, password: str) -> str:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    invalid = AppError(401, "invalid_credentials", "Email o contraseña inválidos")
    if user is None or not user.activo or not verify_password(password, user.password_hash):
        raise invalid
    return create_access_token(user.id_usuario)
