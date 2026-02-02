import uuid
import math
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import (
    ResponseModel, 
    PlannerCreateRequest, 
    PlannerResponse, 
    PlannerUpdateRequest, 
    PaginatedResponseModel
)
from app.models.models import Planner, DayOfWeek, User

router = APIRouter()

@router.post("/", response_model=ResponseModel[PlannerResponse], status_code=status.HTTP_201_CREATED)
async def create_planner(request: PlannerCreateRequest, db: Session = Depends(get_db)):
    day_name = request.plan_date.strftime("%a").upper()
    try:
        day_of_week = DayOfWeek[day_name]
    except KeyError:
        day_of_week = DayOfWeek.MON

    user = db.query(User).first() #임시
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    existing_planner = db.query(Planner).filter(
        Planner.user_id == user.id,
        Planner.plan_date == request.plan_date
    ).first()

    if existing_planner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 {request.plan_date}에 대한 플래너가 존재합니다."
        )

    new_planner = Planner(
        user_id=user.id,
        plan_date=request.plan_date,
        day_of_week=day_of_week,
        daily_goal=0,
        memo=""
    )

    try:
        db.add(new_planner)
        db.commit()
        db.refresh(new_planner)
        return {
            "success": True,
            "data": new_planner
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"플래너 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.put("/{planner_id}", response_model=ResponseModel[PlannerResponse], status_code=status.HTTP_200_OK)
async def update_planner(planner_id: uuid.UUID, request: PlannerUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    planner_query = db.query(Planner).filter(
        Planner.planner_id == planner_id,
        Planner.user_id == user.id
    )
    
    db_planner = planner_query.first()
    
    if not db_planner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="플래너를 찾을 수 없거나 수정 권한이 없습니다."
        )
    
    update_data = request.dict(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="수정할 데이터가 제공되지 않았습니다.")

    try:
        planner_query.update(update_data, synchronize_session='fetch')
        db.commit()
        db.refresh(db_planner)

        return {
            "success": True,
            "data": db_planner
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"업데이트 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{planner_id}", response_model=ResponseModel[PlannerResponse], status_code=status.HTTP_200_OK)
async def get_planner(planner_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    planner = db.query(Planner).filter(
        Planner.planner_id == planner_id,
        Planner.user_id == user.id
    ).first()

    if not planner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="플래너를 찾을 수 없거나 조회 권한이 없습니다."
        )

    return {
        "success": True,
        "data": planner
    }

@router.get("/", response_model=PaginatedResponseModel[PlannerResponse])
async def get_planners(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    query = db.query(Planner).filter(Planner.user_id == user.id)

    if start_date:
        query = query.filter(Planner.plan_date >= start_date)
    if end_date:
        query = query.filter(Planner.plan_date <= end_date)

    total_items = query.count()
    
    limit = min(limit, 100)
    offset = (page - 1) * limit
    
    planners = query.order_by(Planner.plan_date.desc()).offset(offset).limit(limit).all()

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

@router.delete("/{planner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_planner(planner_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    planner_query = db.query(Planner).filter(
        Planner.planner_id == planner_id,
        Planner.user_id == user.id
    )
    
    db_planner = planner_query.first()

    if not db_planner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="플래너를 찾을 수 없거나 삭제 권한이 없습니다."
        )

    try:
        planner_query.delete(synchronize_session=False)
        db.commit()
        return

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"삭제 중 오류가 발생했습니다: {str(e)}"
        )