"""Bearer authentication and role guards."""

from collections.abc import Callable

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import AppError, forbidden
from app.users.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    invalid = AppError(401, "invalid_token", "Credenciales inválidas o expiradas")
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise invalid from exc
    user = db.get(User, user_id)
    if user is None or not user.activo:
        raise invalid
    return user


def require_roles(*names: str) -> Callable[..., User]:
    def guard(user: User = Depends(current_user)) -> User:
        if not any(role.nombre in names for role in user.roles):
            raise forbidden()
        return user

    return guard
