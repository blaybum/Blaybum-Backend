from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.database import get_db
from app.auth.users import current_active_user
from app.models.models import User
from app.schemas.grow_schemas import MonthlyGrowResponse, TodayGrowResponse
from app.schemas.common_schemas import ResponseModel
from app.services.grow_service import grow_service

router = APIRouter()

@router.get("/monthly", response_model=ResponseModel[MonthlyGrowResponse])
async def get_monthly_grow(
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month (1-12)"),
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    records = grow_service.get_monthly_field(db, user, year, month)
    return {
        "success": True,
        "data": {
            "year": year,
            "month": month,
            "records": records
        }
    }

@router.get("/today", response_model=ResponseModel[TodayGrowResponse])
async def get_today_grow(
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    target_date = date.today()
    record = grow_service.calculate_daily_achievement(db, user.id, target_date)
    
    return {
        "success": True,
        "data": record
    }
