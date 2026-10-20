"""Admin user management and a self-profile endpoint."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user, require_roles
from app.core.database import get_db
from app.users import services
from app.users.models import User
from app.users.schemas import UserCreate, UserResponse, UserRoles, UserStatus


router = APIRouter(prefix="/users", tags=["users"])
Admin = Depends(require_roles("ADMINISTRADOR"))


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)) -> UserResponse:
    return services.to_response(user)


@router.post("", response_model=UserResponse, status_code=201)
def create(data: UserCreate, db: Session = Depends(get_db), _admin: User = Admin) -> UserResponse:
    return services.create_user(db, data)


@router.get("", response_model=list[UserResponse])
def list_all(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: User = Admin,
) -> list[UserResponse]:
    return services.list_users(db, offset, limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_one(user_id: int, db: Session = Depends(get_db), _admin: User = Admin) -> UserResponse:
    return services.to_response(services.get_user(db, user_id))


@router.patch("/{user_id}/status", response_model=UserResponse)
def change_status(
    user_id: int, data: UserStatus, db: Session = Depends(get_db), _admin: User = Admin
) -> UserResponse:
    return services.set_status(db, user_id, data.activo)


@router.put("/{user_id}/roles", response_model=UserResponse)
def change_roles(
    user_id: int, data: UserRoles, db: Session = Depends(get_db), _admin: User = Admin
) -> UserResponse:
    return services.set_roles(db, user_id, data.roles)
