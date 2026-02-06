from typing import Dict, List
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
class DailyStatisticsResponse(BaseModel):
    date: date
    total_todos: int
    completed_todos: int
    completion_rate: float
    by_priority: PriorityBreakdown

class WeeklyStatisticsResponse(BaseModel):
    week_start: date
    week_end: date
    total_todos: int
    completed_todos: int
    completion_rate: float
    daily_breakdown: List[DailyBreakdown]