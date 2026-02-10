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
    category: PomoCategory = PomoCategory.ETC

class PomoUpdateRequest(BaseModel):
    todo_id: Optional[uuid.UUID] = None
    category: Optional[PomoCategory] = None
    edit_start_time: Optional[datetime] = None
    edit_end_time: Optional[datetime] = None

# Pomo Response
class PomoResponse(BaseModel):
    id: uuid.UUID
    planner_id: Optional[uuid.UUID] = None
    todo_id: Optional[uuid.UUID] = None
    real_start_time: Optional[datetime] = None
    real_end_time: Optional[datetime] = None
    category: PomoCategory
    distraction_count: int = 0
    edit_start_time: Optional[datetime] = None
    edit_end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PomoCreateResponse(BaseModel):
    id: uuid.UUID
    planner_id: Optional[uuid.UUID] = None
    todo_id: Optional[uuid.UUID] = None
    real_start_time: Optional[datetime] = None
    real_end_time: Optional[datetime] = None
    category: PomoCategory
    distraction_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PomoUpdateResponse(BaseModel):
    id: uuid.UUID
    category: PomoCategory
    distraction_count: int = 0
    edit_start_time: Optional[datetime] = None
    edit_end_time: Optional[datetime] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
