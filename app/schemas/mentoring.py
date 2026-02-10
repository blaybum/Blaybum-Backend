import uuid
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.mentoring_schemas import SubmissionResponse


class AssignmentDetailResponse(BaseModel):
    assignment_id: uuid.UUID
    mentoring_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    grade: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    submissions: List[SubmissionResponse] = []

    model_config = ConfigDict(from_attributes=True)
