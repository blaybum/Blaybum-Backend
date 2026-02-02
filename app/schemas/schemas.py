import uuid
from datetime import datetime, date
from typing import List, Optional, TypeVar, Generic

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