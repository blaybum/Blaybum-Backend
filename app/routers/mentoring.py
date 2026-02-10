import math

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import PaginatedResponseModel
from app.schemas.mentoring_schemas import MentorMenteeResponse
from app.services.mentoring_service import mentoring_service
from app.auth.permissions import get_current_mentor

router = APIRouter()


@router.get("/mentees", response_model=PaginatedResponseModel[MentorMenteeResponse])
async def get_mentee_list(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    mentor: User = Depends(get_current_mentor),
):
    mentees, total_items = mentoring_service.get_mentees(db, mentor, page, limit)
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0

    return {
        "success": True,
        "data": mentees,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items_per_page": limit,
        },
    }
