from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    ResponseModel,
    DailyStatisticsResponse,
    WeeklyStatisticsResponse
)
from app.services.statistics_service import statistics_service
from app.auth.users import current_active_user

router = APIRouter()

@router.get("/daily", response_model=ResponseModel[DailyStatisticsResponse])
async def get_daily_statistics(
    target_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = statistics_service.get_daily_statistics(db, user, target_date)
    return {"success": True, "data": result}

@router.get("/weekly", response_model=ResponseModel[WeeklyStatisticsResponse])
async def get_weekly_statistics(
    start_date: date = Query(..., description="주간 시작 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = statistics_service.get_weekly_statistics(db, user, start_date)
    return {"success": True, "data": result}