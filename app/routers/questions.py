import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common_schemas import ResponseModel
from app.schemas.mentoring_schemas import (QuestionCreateRequest, QuestionAnswerRequest, QuestionResponse)
from app.models import User
from app.services.mentoring_service import mentoring_service
from app.auth.users import current_active_user

router = APIRouter()

@router.get("/", response_model=ResponseModel[List[QuestionResponse]])
async def get_all_questions(db: Session = Depends(get_db),user: User = Depends(current_active_user),):
    result = mentoring_service.get_all_questions(db, user)
    return {"success": True, "data": result}

@router.post("/{question_id}/answer", response_model=ResponseModel[QuestionResponse])
async def answer_question(question_id: uuid.UUID,request: QuestionAnswerRequest,db: Session = Depends(get_db),user: User = Depends(current_active_user),):
    result = mentoring_service.answer_question_direct(db, user, question_id, request)
    return {"success": True, "data": result}