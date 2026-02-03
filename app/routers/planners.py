import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import (
    ResponseModel, 
    PlannerCreateRequest, 
    PlannerResponse, 
    PlannerUpdateRequest, 
    PaginatedResponseModel
)
from app.models.models import User
from app.services.planner_service import planner_service

router = APIRouter()

# Temporary: Helper to get the first user until auth is implemented
def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return user

@router.post("/", response_model=ResponseModel[PlannerResponse], status_code=status.HTTP_201_CREATED)
async def create_planner(
    request: PlannerCreateRequest, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = planner_service.create_planner(db, user, request)
    return {"success": True, "data": result}

@router.get("/{planner_id}", response_model=ResponseModel[PlannerResponse], status_code=status.HTTP_200_OK)
async def get_planner(
    planner_id: uuid.UUID, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = planner_service.get_planner(db, user, planner_id)
    return {"success": True, "data": result}

@router.get("/", response_model=PaginatedResponseModel[PlannerResponse])
async def get_planners(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    from datetime import date # Need this for type hint
    planners, total_items = planner_service.get_planners(db, user, start_date, end_date, page, limit)
    
    import math
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0

    return {
        "success": True,
        "data": planners,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items_per_page": limit
        }
    }

@router.put("/{planner_id}", response_model=ResponseModel[PlannerResponse], status_code=status.HTTP_200_OK)
async def update_planner(
    planner_id: uuid.UUID, 
    request: PlannerUpdateRequest, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = planner_service.update_planner(db, user, planner_id, request)
    return {"success": True, "data": result}

@router.delete("/{planner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_planner(
    planner_id: uuid.UUID, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    planner_service.delete_planner(db, user, planner_id)
    return