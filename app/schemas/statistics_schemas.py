from typing import Dict, List
from pydantic import BaseModel
from datetime import date

#Sub
class PriorityStat(BaseModel):
    total: int
    completed: int

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
    by_priority: Dict[str, PriorityStat]

class WeeklyStatisticsResponse(BaseModel):
    week_start: date
    week_end: date
    total_todos: int
    completed_todos: int
    completion_rate: float
    daily_breakdown: List[DailyBreakdown]