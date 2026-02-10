import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from .common_schemas import PaginationInfo


# ===== Mentoring Request =====

class MentoringAcceptRequest(BaseModel):
    message: Optional[str] = None

class MentoringRejectRequest(BaseModel):
    reason: Optional[str] = None

class MentoringStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern="^(DURING|END)$")


# ===== Mentoring Response =====

class MentoringRequestItem(BaseModel):
    mentoring_id: uuid.UUID
    mentee_id: uuid.UUID
    mentee_name: Optional[str] = None
    mentee_email: Optional[str] = None
    requested_at: Optional[datetime] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class MentoringRequestListResponse(BaseModel):
    requests: List[MentoringRequestItem]
    pagination: PaginationInfo

class MentoringAcceptResponse(BaseModel):
    mentoring_id: uuid.UUID
    status: str
    started_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MentoringStatusResponse(BaseModel):
    mentoring_id: uuid.UUID
    status: str
    ended_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    message: str


# ===== Mentee Info =====

class RecentActivity(BaseModel):
    last_login: Optional[datetime] = None
    completed_todos: int = 0
    pending_assignments: int = 0

class MenteeDetailResponse(BaseModel):
    mentee_id: uuid.UUID
    name: Optional[str] = None
    email: Optional[str] = None
    profile_image: Optional[str] = None
    mentoring_id: uuid.UUID
    mentoring_status: str
    started_at: Optional[datetime] = None
    total_study_time: int = 0
    recent_activity: RecentActivity

    model_config = ConfigDict(from_attributes=True)


# ===== Assignment =====

class AssignmentCreateRequest(BaseModel):
    mentoring_id: uuid.UUID
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class AssignmentUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class AssignmentGradeRequest(BaseModel):
    grade: int = Field(..., ge=0, le=100)
    comment: Optional[str] = None

class AssignmentListItem(BaseModel):
    assignment_id: uuid.UUID
    mentoring_id: uuid.UUID
    mentee_name: Optional[str] = None
    title: str
    due_date: Optional[datetime] = None
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AssignmentListResponse(BaseModel):
    assignments: List[AssignmentListItem]
    pagination: PaginationInfo

class SubmissionResponse(BaseModel):
    submission_id: uuid.UUID
    content: Optional[str] = None
    file_url: Optional[str] = None
    submitted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AssignmentDetailResponse(BaseModel):
    assignment_id: uuid.UUID
    mentoring_id: uuid.UUID
    mentee_id: Optional[uuid.UUID] = None
    mentee_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    grade: Optional[int] = None
    created_at: Optional[datetime] = None
    submission: Optional[SubmissionResponse] = None

    model_config = ConfigDict(from_attributes=True)

class AssignmentCreateResponse(BaseModel):
    assignment_id: uuid.UUID
    mentoring_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AssignmentUpdateResponse(BaseModel):
    assignment_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AssignmentGradeResponse(BaseModel):
    assignment_id: uuid.UUID
    grade: int
    status: str
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ===== Question =====

class QuestionAnswerRequest(BaseModel):
    answer: str

class QuestionListItem(BaseModel):
    question_id: uuid.UUID
    mentoring_id: uuid.UUID
    mentee_name: Optional[str] = None
    question: str
    is_answered: bool
    asked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class QuestionListResponse(BaseModel):
    questions: List[QuestionListItem]
    pagination: PaginationInfo

class QuestionAnswerResponse(BaseModel):
    question_id: uuid.UUID
    question: str
    answer: str
    is_answered: bool
    answered_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ===== Feedback =====

class FeedbackCreateRequest(BaseModel):
    content: str

class FeedbackListItem(BaseModel):
    feedback_id: uuid.UUID
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class FeedbackListResponse(BaseModel):
    feedbacks: List[FeedbackListItem]
    pagination: PaginationInfo

class FeedbackCreateResponse(BaseModel):
    feedback_id: uuid.UUID
    mentoring_id: uuid.UUID
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ===== Statistics =====

class DailyStudyTime(BaseModel):
    date: str
    minutes: int

class AssignmentStats(BaseModel):
    total: int = 0
    completed: int = 0
    pending: int = 0
    average_grade: Optional[float] = None

class TodoStats(BaseModel):
    total: int = 0
    completed: int = 0
    completion_rate: float = 0

class MenteeStatisticsResponse(BaseModel):
    period: str
    total_study_time: int = 0
    daily_study_time: List[DailyStudyTime] = []
    assignments: AssignmentStats
    todos: TodoStats
