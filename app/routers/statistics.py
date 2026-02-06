from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models import User
from app.schemas import (
    ResponseModel,
    DailyStatisticsResponse,
    WeeklyStatisticsResponse
)
from app.services import statistics_service

router = APIRouter()

def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return user

@router.get("/planner/daily", response_model=ResponseModel[DailyStatisticsResponse])
async def get_planner_daily_statistics(
    target_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = statistics_service.get_planner_daily_statistics(db, user, target_date)
    return {"success": True, "data": result}

@router.get("/planner/weekly", response_model=ResponseModel[WeeklyStatisticsResponse])
async def get_planner_weekly_statistics(
    start_date: date = Query(..., description="주간 시작 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = statistics_service.get_planner_weekly_statistics(db, user, start_date)
    return {"success": True, "data": result}