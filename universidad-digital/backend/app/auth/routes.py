"""OAuth2 password form for Swagger and API clients."""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import services
from app.auth.schemas import TokenResponse
from app.core.database import get_db


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def token(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> TokenResponse:
    return TokenResponse(access_token=services.login(db, form.username, form.password))
