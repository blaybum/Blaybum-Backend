from typing import Optional, List
from datetime import datetime, time
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
import uuid
class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TodoOrder(BaseModel):
    todo_id: uuid.UUID
    order_index: int
class TodoCreateRequest(BaseModel):
    planner_id: uuid.UUID
    title: str
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=0)
    priority: PriorityEnum = Field(PriorityEnum.medium)

class TodoUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_time: Optional[time] = None
    estimated_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[str] = None

class TodoReorderRequest(BaseModel):
    planner_id: uuid.UUID
    orders: List[TodoOrder]

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
    has_image: bool = False
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
