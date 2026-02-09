from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models import User
from app.schemas import (
    ResponseModel,
    PlannerDailyStatisticsResponse,
    PlannerWeeklyStatisticsResponse,
    PomoDailyStatisticsResponse,
    PomoMeStatisticsResponse
)
from app.services.statistics_service import statistics_service
from app.auth.users import current_active_user

router = APIRouter()

def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    return user

@router.get("/daily", response_model=ResponseModel[DailyStatisticsResponse])
async def get_daily_statistics(
    target_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = statistics_service.get_planner_daily_statistics(db, user, target_date)
    return {"success": True, "data": result}

@router.get("/planner/weekly", response_model=ResponseModel[PlannerWeeklyStatisticsResponse])
async def get_planner_weekly_statistics(
    start_date: date = Query(..., description="주간 시작 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = statistics_service.get_planner_weekly_statistics(db, user, start_date)
    return {"success": True, "data": result}

@router.get("/pomo/daily", response_model=ResponseModel[PomoDailyStatisticsResponse])
async def get_pomo_daily_statistics(
    target_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = statistics_service.get_pomo_daily_statistics(db, user, target_date)
    return {"success": True, "data": result}

@router.get("/pomo/me", response_model=ResponseModel[PomoMeStatisticsResponse])
async def get_pomo_me_statistics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = statistics_service.get_pomo_me_statistics(db, user)
    return {"success": True, "data": result}