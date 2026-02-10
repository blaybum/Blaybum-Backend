import uuid
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common_schemas import ResponseModel, PaginatedResponseModel
from app.schemas.mentoring_schemas import (
    MentoringCreateRequest, MentoringStatusUpdateRequest, MentoringResponse,
    FeedbackCreateRequest, FeedbackResponse,
    MentoringRequestResponse, MenteeDetailResponse, MenteeStatisticsResponse,
    AssignmentCreateRequest, AssignmentUpdateRequest, AssignmentResponse,
    AssignmentGradeRequest, QuestionResponse, QuestionAnswerRequest,
    SubmissionResponse
)
from app.schemas.mentoring import AssignmentDetailResponse
from app.models import User
from app.services.mentoring_service import mentoring_service
from app.auth.users import current_active_user
from app.auth.permissions import get_current_mentor

router = APIRouter()

@router.post("/requests", response_model=ResponseModel[MentoringResponse], status_code=status.HTTP_201_CREATED)
async def create_mentoring_request(
    request: MentoringCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = mentoring_service.create_mentoring_request(db, user, request)
    return {"success": True, "data": result}


@router.get("/requests", response_model=ResponseModel[List[MentoringRequestResponse]])
async def get_mentoring_requests(
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = mentoring_service.get_mentoring_requests(db, user)
    return {"success": True, "data": result}


@router.post("/requests/{mentoring_id}/accept", response_model=ResponseModel[MentoringResponse])
async def accept_mentoring_request(
    mentoring_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = mentoring_service.accept_mentoring_request(db, user, mentoring_id)
    return {"success": True, "data": result}


@router.post("/requests/{mentoring_id}/reject", response_model=ResponseModel[MentoringResponse])
async def reject_mentoring_request(
    mentoring_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = mentoring_service.reject_mentoring_request(db, user, mentoring_id)
    return {"success": True, "data": result}


# ============================================================
# 멘티 관리
# ============================================================

@router.get("/mentees", response_model=ResponseModel[List[MenteeDetailResponse]])
async def get_mentees(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    """멘토의 멘티 목록 조회"""
    mentorings = mentoring_service.get_mentees(db, user)
    data = [
        MenteeDetailResponse(
            mentee_id=m.mentee.id,
            username=m.mentee.username,
            full_name=m.mentee.full_name,
            profile_image=m.mentee.profile_image,
            mentoring_id=m.mentoring_id,
            status=m.status,
            started_at=m.started_at,
        )
        for m in mentorings
    ]
    return {"success": True, "data": data}


@router.get("/mentees/{mentee_id}", response_model=ResponseModel[MenteeDetailResponse])
async def get_mentee_detail(
    mentee_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = mentoring_service.get_mentee_detail(db, user, mentee_id)
    return {"success": True, "data": result}


@router.get("/mentees/{mentee_id}/statistics", response_model=ResponseModel[MenteeStatisticsResponse])
async def get_mentee_statistics(
    mentee_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = mentoring_service.get_mentee_statistics(db, user, mentee_id)
    return {"success": True, "data": result}


@router.post(
    "/mentees/{mentee_id}/feedback",
    response_model=ResponseModel[FeedbackResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_mentee_feedback(
    mentee_id: uuid.UUID,
    request: FeedbackCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = mentoring_service.create_mentee_feedback(db, user, mentee_id, request)
    return {"success": True, "data": result}


@router.get("/mentees/{mentee_id}/feedbacks", response_model=ResponseModel[List[FeedbackResponse]])
async def get_mentee_feedbacks(
    mentee_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = mentoring_service.get_mentee_feedbacks(db, user, mentee_id)
    return {"success": True, "data": result}

@router.post(
    "/assignments",
    response_model=ResponseModel[AssignmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(
    request: AssignmentCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    """과제 생성 (멘토 전용)"""
    result = mentoring_service.create_assignment_direct(db, user, request)
    return {"success": True, "data": result}


@router.get("/assignments", response_model=ResponseModel[List[AssignmentResponse]])
async def get_assignments(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    """멘토가 배정한 과제 목록 조회"""
    result = mentoring_service.get_all_assignments(db, user)
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
    """과제 상세 조회 (제출물 포함)"""
    result = mentoring_service.get_assignment_detail(db, user, assignment_id)
    return {"success": True, "data": result}


@router.patch(
    "/assignments/{assignment_id}",
    response_model=ResponseModel[AssignmentResponse],
)
async def update_assignment(
    assignment_id: uuid.UUID,
    request: AssignmentUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    """과제 수정 (멘토 전용)"""
    result = mentoring_service.update_assignment_direct(db, user, assignment_id, request)
    return {"success": True, "data": result}


@router.delete(
    "/assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_assignment(
    assignment_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    """과제 삭제 (멘토 전용)"""
    mentoring_service.delete_assignment_direct(db, user, assignment_id)


@router.patch(
    "/assignments/{assignment_id}/grade",
    response_model=ResponseModel[AssignmentResponse],
)
async def grade_assignment(
    assignment_id: uuid.UUID,
    request: AssignmentGradeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    """과제 채점 (멘토 전용)"""
    result = mentoring_service.grade_assignment(db, user, assignment_id, request)
    return {"success": True, "data": result}


# ============================================================
# 질문 관리 (Question)
# ============================================================

@router.get("/questions", response_model=ResponseModel[List[QuestionResponse]])
async def get_questions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    """멘토에게 온 질문 목록 조회"""
    result = mentoring_service.get_all_questions(db, user)
    return {"success": True, "data": result}


@router.post(
    "/questions/{question_id}/answer",
    response_model=ResponseModel[QuestionResponse],
)
async def answer_question(
    question_id: uuid.UUID,
    request: QuestionAnswerRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_mentor),
):
    """질문 답변 (멘토 전용)"""
    result = mentoring_service.answer_question_direct(db, user, question_id, request)
    return {"success": True, "data": result}

@router.put("/{mentoring_id}/status", response_model=ResponseModel[MentoringResponse])
async def update_mentoring_status(
    mentoring_id: uuid.UUID,
    request: MentoringStatusUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = mentoring_service.update_mentoring_status(db, user, mentoring_id, request)
    return {"success": True, "data": result}


@router.delete("/{mentoring_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mentoring(
    mentoring_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user),
):
    mentoring_service.delete_mentoring(db, user, mentoring_id)
