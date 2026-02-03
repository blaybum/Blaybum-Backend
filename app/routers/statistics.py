from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta  # timedelta 추가
from typing import List

from app.database import get_db
from app.models.models import Todo, Planner, User
from app.schemas.schemas import (
    ResponseModel, 
    DailyStatisticsResponse, 
    WeeklyStatisticsResponse
)

router = APIRouter()

@router.get("/daily", response_model=ResponseModel[DailyStatisticsResponse])
async def get_daily_statistics(
    target_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db)
):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    todos = db.query(Todo).join(Planner).filter(
        Planner.user_id == user.id,
        Planner.plan_date == target_date
    ).all()

    stats = {
        "date": target_date,
        "total_todos": 0,
        "completed_todos": 0,
        "completion_rate": 0.0,
        "by_priority": {
            "high": {"total": 0, "completed": 0},
            "medium": {"total": 0, "completed": 0},
            "low": {"total": 0, "completed": 0}
        }
    }

    if not todos:
        return {"success": True, "data": stats}

    stats["total_todos"] = len(todos)
    stats["completed_todos"] = len([t for t in todos if t.status == "completed"])
    stats["completion_rate"] = round((stats["completed_todos"] / stats["total_todos"]) * 100, 2)

    for todo in todos:
        p = todo.priority if todo.priority in stats["by_priority"] else "medium"
        stats["by_priority"][p]["total"] += 1
        if todo.status == "completed":
            stats["by_priority"][p]["completed"] += 1

    return {"success": True, "data": stats}


@router.get("/weekly", response_model=ResponseModel[WeeklyStatisticsResponse])
async def get_weekly_statistics(
    start_date: date = Query(..., description="주간 시작 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    end_date = start_date + timedelta(days=6)

    results = db.query(Todo, Planner.plan_date).join(Planner).filter(
        Planner.user_id == user.id,
        Planner.plan_date >= start_date,
        Planner.plan_date <= end_date
    ).all()

    total_todos = len(results)
    completed_todos = len([t for t, d in results if t.status == "completed"])
    completion_rate = round((completed_todos / total_todos) * 100, 2) if total_todos > 0 else 0.0

    breakdown_dict = { (start_date + timedelta(days=i)): {"total": 0, "completed": 0} for i in range(7) }

    for todo, plan_date in results:
        if plan_date in breakdown_dict:
            breakdown_dict[plan_date]["total"] += 1
            if todo.status == "completed":
                breakdown_dict[plan_date]["completed"] += 1

    daily_breakdown = [
        {"date": d, "total": s["total"], "completed": s["completed"]}
        for d, s in sorted(breakdown_dict.items())
    ]

    return {
        "success": True,
        "data": {
            "week_start": start_date,
            "week_end": end_date,
            "total_todos": total_todos,
            "completed_todos": completed_todos,
            "completion_rate": completion_rate,
            "daily_breakdown": daily_breakdown
        }
    }