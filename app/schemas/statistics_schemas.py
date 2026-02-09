from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import date

#Sub
class PriorityStat(BaseModel):
    total: int = 0
    completed: int = 0

class PriorityBreakdown(BaseModel):
    high: PriorityStat = PriorityStat()
    medium: PriorityStat = PriorityStat()
    low: PriorityStat = PriorityStat()

class DailyBreakdown(BaseModel):
    date: date
    total: int
    completed: int

#Response
class PlannerDailyStatisticsResponse(BaseModel):
    date: date
    total_todos: int
    completed_todos: int
    completion_rate: float
    by_priority: PriorityBreakdown

class PlannerWeeklyStatisticsResponse(BaseModel):
    week_start: date
    week_end: date
    total_todos: int
    completed_todos: int
    completion_rate: float
    daily_breakdown: List[DailyBreakdown]

class PomoDailyStatisticsResponse(BaseModel):
    date: date
    total_study_time_minutes: int
    pomo_count: int
    completed_todos: int
    total_distraction_count: int = 0

class PomoMeStatisticsResponse(BaseModel):
    total_study_time_minutes: int
    average_daily_minutes: int
    total_pomo_count: int
    total_distraction_count: int = 0
    best_day: Optional[date] = None