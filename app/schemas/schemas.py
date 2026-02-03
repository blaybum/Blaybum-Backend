import uuid
from datetime import datetime, date, time
from enum import Enum
from typing import List, Optional, TypeVar, Generic,Dict

from pydantic import BaseModel, ConfigDict,Field

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None

class PlannerCreateRequest(BaseModel):
    plan_date: date

class PlannerResponse(BaseModel):
    planner_id: uuid.UUID
    plan_date: date
    day_of_week: str
    daily_goal: Optional[int] = 0
    memo: Optional[str] = ""
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PlannerUpdateRequest(BaseModel):
    daily_goal: Optional[int] = Field(None, ge=0, le=100)
    memo: Optional[str] = None

class PaginationInfo(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int

class PaginatedResponseModel(BaseModel, Generic[T]):
    success: bool
    data: List[T]
    pagination: PaginationInfo

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TodoCreateRequest(BaseModel):
    planner_id: uuid.UUID
    title: str
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)
    priority: PriorityEnum = Field(PriorityEnum.medium)

class TodoResponse(BaseModel):
    todo_id: uuid.UUID
    planner_id: uuid.UUID
    title: str
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    priority: PriorityEnum
    status: str
    estimated_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    completed_at: Optional[datetime] = None
    order_index: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            time: lambda v: v.strftime("%H:%M:%S")
        }

class TodoUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    estimated_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[str] = None

class PriorityStat(BaseModel):
    total: int
    completed: int

class DailyStatisticsResponse(BaseModel):
    date: date
    total_todos: int
    completed_todos: int
    completion_rate: float
    by_priority: Dict[str, PriorityStat]

class DailyBreakdown(BaseModel):
    date: date
    total: int
    completed: int

class WeeklyStatisticsResponse(BaseModel):
    week_start: date
    week_end: date
    total_todos: int
    completed_todos: int
    completion_rate: float
    daily_breakdown: List[DailyBreakdown]