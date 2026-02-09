import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models import PomoCategory

# Enum
class UsageEventTypeEnum(str, Enum):
    PICK_UP = "PICK_UP"
    PUT_DOWN = "PUT_DOWN"

# Concentration Request
class ConcentrationCreate(BaseModel):
    event_type: UsageEventTypeEnum
    timestamp: Optional[datetime] = None

# Concentration Response
class ConcentrationResponse(BaseModel):
    id: uuid.UUID
    pomo_id: uuid.UUID
    event_type: UsageEventTypeEnum
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Pomo Request
class PomoCreateRequest(BaseModel):
    planner_id: Optional[uuid.UUID] = None
    todo_id: Optional[uuid.UUID] = None
    real_start_time: Optional[datetime] = None
    real_end_time: Optional[datetime] = None
    category: str = "기타"

class PomoUpdateRequest(BaseModel):
    todo_id: Optional[uuid.UUID] = None
    category: Optional[str] = None
    edit_start_time: Optional[datetime] = None
    edit_end_time: Optional[datetime] = None

# Pomo Response
class PomoResponse(BaseModel):
    id: uuid.UUID
    planner_id: Optional[uuid.UUID] = None
    todo_id: Optional[uuid.UUID] = None
    real_start_time: datetime
    real_end_time: datetime
    category: str
    edit_start_time: datetime
    edit_end_time: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PomoCreateResponse(BaseModel):
    id: uuid.UUID
    planner_id: Optional[uuid.UUID] = None
    todo_id: Optional[uuid.UUID] = None
    real_start_time: datetime
    real_end_time: datetime
    category: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PomoUpdateResponse(BaseModel):
    id: uuid.UUID
    edit_start_time: datetime
    edit_end_time: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
