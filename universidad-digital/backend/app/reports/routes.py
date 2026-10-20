"""Period report endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user
from app.core.database import get_db
from app.reports import services
from app.reports.schemas import SubjectReport
from app.users.models import User


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/periods/{period_id}/subjects", response_model=list[SubjectReport])
def period_subjects(
    period_id: int, db: Session = Depends(get_db), actor: User = Depends(current_user)
) -> list[SubjectReport]:
    return services.by_period(db, period_id, actor)
