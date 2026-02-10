import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.models import MentoringStatus, AssignmentStatus

class MentoringCreateRequest(BaseModel):
    mentor_id: uuid.UUID

class MentoringStatusUpdateRequest(BaseModel):
    status: MentoringStatus

class MentoringResponse(BaseModel):
    mentoring_id: uuid.UUID
    mentee_id: uuid.UUID
    mentor_id: uuid.UUID
    status: MentoringStatus
    requested_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AssignmentCreateRequest(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    mentee_id: uuid.UUID 

class AssignmentUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[AssignmentStatus] = None
    grade: Optional[int] = Field(None, ge=0, le=100)

class AssignmentResponse(BaseModel):
    assignment_id: uuid.UUID
    mentoring_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: AssignmentStatus
    grade: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SubmissionCreateRequest(BaseModel):
    content: Optional[str] = None
    file_url: Optional[str] = Field(None, max_length=500)

class SubmissionResponse(BaseModel):
    submission_id: uuid.UUID
    assignment_id: uuid.UUID
    content: Optional[str] = None
    file_url: Optional[str] = None
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionCreateRequest(BaseModel):
    question: str

class QuestionAnswerRequest(BaseModel):
    answer: str

class QuestionResponse(BaseModel):
    question_id: uuid.UUID
    mentoring_id: uuid.UUID
    question: str
    answer: Optional[str] = None
    is_answered: bool
    asked_at: datetime
    answered_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackCreateRequest(BaseModel):
    content: str

class FeedbackResponse(BaseModel):
    feedback_id: uuid.UUID
    mentoring_id: uuid.UUID
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AssignmentGradeRequest(BaseModel):
    grade: int = Field(..., ge=0, le=100)
    feedback: Optional[str] = None

class MentoringRequestResponse(BaseModel):
    mentoring_id: uuid.UUID
    mentee_id: uuid.UUID
    mentor_id: uuid.UUID
    status: MentoringStatus
    requested_at: datetime
    mentee_name: Optional[str] = None
    mentee_profile_image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class MenteeDetailResponse(BaseModel):
    mentee_id: uuid.UUID
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    mentoring_id: uuid.UUID
    status: MentoringStatus
    started_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class MenteeStatisticsResponse(BaseModel):
    mentee_id: uuid.UUID
    total_assignments: int
    completed_assignments: int
    pending_assignments: int
    average_grade: Optional[float] = None
    total_questions: int
    answered_questions: int
    total_feedbacks: int
    last_activity: Optional[datetime] = None
