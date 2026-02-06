import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Enum
class UsageEventTypeEnum(str, Enum):
    PICK_UP = "PICK_UP"
    PUT_DOWN = "PUT_DOWN"

# Pomo Request
class PomoCreateRequest(BaseModel):
    planner_id: Optional[uuid.UUID] = None
    todo_id: Optional[uuid.UUID] = None
    real_start_time: Optional[datetime] = None
    real_end_time: Optional[datetime] = None

class PomoUpdateRequest(BaseModel):
    todo_id: Optional[uuid.UUID] = None
    edit_start_time: Optional[datetime] = None
    edit_end_time: Optional[datetime] = None

# Pomo Response
class PomoResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    planner_id: Optional[uuid.UUID] = None
    todo_id: Optional[uuid.UUID] = None
    real_start_time: datetime
    real_end_time: datetime
    edit_start_time: datetime
    edit_end_time: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
