from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field
import uuid

#Request
class PlannerCreateRequest(BaseModel):
    plan_date: date
    
class PlannerUpdateRequest(BaseModel):
    daily_goal: Optional[int] = Field(None, ge=0, le=100)
    memo: Optional[str] = None

#Response
class PlannerResponse(BaseModel):
    planner_id: uuid.UUID
    plan_date: date
    day_of_week: str
    daily_goal: Optional[int] = 0
    memo: Optional[str] = ""
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)