import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MenteeResponse(BaseModel):
    id: uuid.UUID
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MentorMenteeResponse(BaseModel):
    id: uuid.UUID
    mentor_id: uuid.UUID
    mentee_id: uuid.UUID
    mentee: MenteeResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
