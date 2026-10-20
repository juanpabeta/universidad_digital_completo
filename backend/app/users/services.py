"""User provisioning, role assignment and account status."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import conflict, not_found
from app.core.security import hash_password
from app.users.models import Role, User
from app.users.schemas import UserCreate, UserResponse


ROLE_NAMES = frozenset({"ADMINISTRADOR", "DOCENTE", "ESTUDIANTE"})


def _roles(db: Session, names: list[str]) -> list[Role]:
    requested = set(names)
    if not requested or not requested <= ROLE_NAMES:
        raise conflict("Los roles deben ser ADMINISTRADOR, DOCENTE o ESTUDIANTE")
    found = list(db.scalars(select(Role).where(Role.nombre.in_(requested))))
    if len(found) != len(requested):
        raise conflict("Faltan roles iniciales; ejecute el comando de bootstrap")
    return found


def to_response(user: User) -> UserResponse:
    return UserResponse(
        id_usuario=user.id_usuario,
        nombres=user.nombres,
        apellidos=user.apellidos,
        email=user.email,
        activo=user.activo,
        fecha_creacion=user.fecha_creacion,
        roles=sorted(role.nombre for role in user.roles),
    )


def create_user(db: Session, data: UserCreate) -> UserResponse:
    user = User(
        nombres=data.nombres.strip(),
        apellidos=data.apellidos.strip(),
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
        roles=_roles(db, data.roles),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("El email ya está registrado") from exc
    db.refresh(user)
    return to_response(user)


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise not_found("Usuario")
    return user


def list_users(db: Session, offset: int, limit: int) -> list[UserResponse]:
    users = db.scalars(select(User).order_by(User.id_usuario).offset(offset).limit(limit))
    return [to_response(user) for user in users]


def set_status(db: Session, user_id: int, active: bool) -> UserResponse:
    user = get_user(db, user_id)
    user.activo = active
    db.commit()
    db.refresh(user)
    return to_response(user)


def set_roles(db: Session, user_id: int, names: list[str]) -> UserResponse:
    user = get_user(db, user_id)
    user.roles = _roles(db, names)
    db.commit()
    db.refresh(user)
    return to_response(user)
