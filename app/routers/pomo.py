import uuid
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import ResponseModel, PaginatedResponseModel
from app.schemas import (
    PomoCreateRequest, 
    PomoResponse, 
    PomoUpdateRequest,
    ConcentrationCreate,
    ConcentrationResponse
)
from app.services import pomo_service

router = APIRouter()

def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return user

@router.post("/", response_model=ResponseModel[PomoResponse], status_code=status.HTTP_201_CREATED)
async def create_pomo(
    request: PomoCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = pomo_service.create_pomo(db, user, request)
    return {"success": True, "data": result}

@router.get("/", response_model=PaginatedResponseModel[PomoResponse])
async def get_pomos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    pomos, total_items = pomo_service.get_pomos(db, user, page, limit)
    
    import math
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    
    return {
        "success": True,
        "data": pomos,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items_per_page": limit
        }
    }

@router.get("/{pomo_id}", response_model=ResponseModel[PomoResponse])
async def get_pomo(
    pomo_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = pomo_service.get_pomo(db, user, pomo_id)
    return {"success": True, "data": result}

@router.patch("/{pomo_id}", response_model=ResponseModel[PomoResponse])
async def update_pomo(
    pomo_id: uuid.UUID,
    request: PomoUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = pomo_service.update_pomo(db, user, pomo_id, request)
    return {"success": True, "data": result}

@router.delete("/{pomo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pomo(
    pomo_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    pomo_service.delete_pomo(db, user, pomo_id)
    return

@router.post("/{pomo_id}/concentration", response_model=ResponseModel[ConcentrationResponse], status_code=status.HTTP_201_CREATED)
async def add_concentration_log(
    pomo_id: uuid.UUID,
    request: ConcentrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = pomo_service.add_concentration_log(db, user, pomo_id, request)
    return {"success": True, "data": result}
