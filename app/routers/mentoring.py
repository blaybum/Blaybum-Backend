import uuid
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ResponseModel,
    MessageResponse,
    MentoringAcceptRequest,
    MentoringRejectRequest,
    MentoringStatusUpdateRequest,
    MentoringRequestListResponse,
    MentoringAcceptResponse,
    MentoringStatusResponse,
    MenteeDetailResponse,
    AssignmentCreateRequest,
    AssignmentUpdateRequest,
    AssignmentGradeRequest,
    AssignmentListResponse,
    AssignmentDetailResponse,
    AssignmentCreateResponse,
    AssignmentUpdateResponse,
    AssignmentGradeResponse,
    QuestionAnswerRequest,
    QuestionListResponse,
    QuestionAnswerResponse,
    FeedbackCreateRequest,
    FeedbackListResponse,
    FeedbackCreateResponse,
    MenteeStatisticsResponse,
)
from app.models.models import User
from app.services.mentoring_service import mentoring_service
from app.auth.permissions import get_current_mentor

router = APIRouter()


# ===== 멘토링 신청 관리 =====

@router.get("/requests", response_model=ResponseModel[MentoringRequestListResponse])
async def get_mentoring_requests(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.get_mentoring_requests(db, user, page=page, limit=limit, status_filter=status)
    return {"success": True, "data": result}


@router.post(
    "/requests/{mentoring_id}/accept",
    response_model=ResponseModel[MentoringAcceptResponse],
)
async def accept_mentoring_request(
    mentoring_id: uuid.UUID,
    request: MentoringAcceptRequest = MentoringAcceptRequest(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.accept_request(db, user, mentoring_id, request)
    return {"success": True, "data": result}


@router.post(
    "/requests/{mentoring_id}/reject",
    response_model=ResponseModel[MessageResponse],
)
async def reject_mentoring_request(
    mentoring_id: uuid.UUID,
    request: MentoringRejectRequest = MentoringRejectRequest(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.reject_request(db, user, mentoring_id, request)
    return {"success": True, "data": result}


# ===== 멘토링 상태 관리 =====

@router.patch(
    "/{mentoring_id}/status",
    response_model=ResponseModel[MentoringStatusResponse],
)
async def update_mentoring_status(
    mentoring_id: uuid.UUID,
    request: MentoringStatusUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.update_status(db, user, mentoring_id, request)
    return {"success": True, "data": result}


@router.delete(
    "/{mentoring_id}",
    response_model=ResponseModel[MessageResponse],
)
async def delete_mentoring(
    mentoring_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.delete_mentoring(db, user, mentoring_id)
    return {"success": True, "data": result}


# ===== 멘티 정보 =====

@router.get(
    "/mentees/{mentee_id}",
    response_model=ResponseModel[MenteeDetailResponse],
)
async def get_mentee_detail(
    mentee_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.get_mentee_detail(db, user, mentee_id)
    return {"success": True, "data": result}


@router.get(
    "/mentees/{mentee_id}/statistics",
    response_model=ResponseModel[MenteeStatisticsResponse],
)
async def get_mentee_statistics(
    mentee_id: uuid.UUID,
    period: str = "week",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.get_mentee_statistics(db, user, mentee_id, period=period)
    return {"success": True, "data": result}


# ===== 과제 관리 =====

@router.get("/assignments", response_model=ResponseModel[AssignmentListResponse])
async def get_assignments(
    mentoring_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.get_assignments(
        db, user, mentoring_id=mentoring_id, status_filter=status, page=page, limit=limit
    )
    return {"success": True, "data": result}


@router.get(
    "/assignments/{assignment_id}",
    response_model=ResponseModel[AssignmentDetailResponse],
)
async def get_assignment_detail(
    assignment_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.get_assignment_detail(db, user, assignment_id)
    return {"success": True, "data": result}


@router.post(
    "/assignments",
    response_model=ResponseModel[AssignmentCreateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(
    request: AssignmentCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.create_assignment(db, user, request)
    return {"success": True, "data": result}


@router.patch(
    "/assignments/{assignment_id}",
    response_model=ResponseModel[AssignmentUpdateResponse],
)
async def update_assignment(
    assignment_id: uuid.UUID,
    request: AssignmentUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.update_assignment(db, user, assignment_id, request)
    return {"success": True, "data": result}


@router.delete("/assignments/{assignment_id}", response_model=ResponseModel[MessageResponse])
async def delete_assignment(
    assignment_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.delete_assignment(db, user, assignment_id)
    return {"success": True, "data": result}


@router.patch(
    "/assignments/{assignment_id}/grade",
    response_model=ResponseModel[AssignmentGradeResponse],
)
async def grade_assignment(
    assignment_id: uuid.UUID,
    request: AssignmentGradeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.grade_assignment(db, user, assignment_id, request)
    return {"success": True, "data": result}


# ===== 질문 관리 =====

@router.get("/questions", response_model=ResponseModel[QuestionListResponse])
async def get_questions(
    mentoring_id: Optional[uuid.UUID] = None,
    is_answered: Optional[bool] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.get_questions(
        db, user, mentoring_id=mentoring_id, is_answered=is_answered, page=page, limit=limit
    )
    return {"success": True, "data": result}


@router.post(
    "/questions/{question_id}/answer",
    response_model=ResponseModel[QuestionAnswerResponse],
)
async def answer_question(
    question_id: uuid.UUID,
    request: QuestionAnswerRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.answer_question(db, user, question_id, request)
    return {"success": True, "data": result}


# ===== 피드백 관리 =====

@router.get(
    "/mentees/{mentee_id}/feedbacks",
    response_model=ResponseModel[FeedbackListResponse],
)
async def get_feedbacks(
    mentee_id: uuid.UUID,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.get_feedbacks(db, user, mentee_id, page=page, limit=limit)
    return {"success": True, "data": result}


@router.post(
    "/mentees/{mentee_id}/feedback",
    response_model=ResponseModel[FeedbackCreateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback(
    mentee_id: uuid.UUID,
    request: FeedbackCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    result = mentoring_service.create_feedback(db, user, mentee_id, request)
    return {"success": True, "data": result}
