import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common_schemas import ResponseModel
from app.schemas.mentoring_schemas import (AssignmentCreateRequest, AssignmentUpdateRequest, AssignmentResponse,AssignmentGradeRequest)
from app.models import User
from app.services.mentoring_service import mentoring_service
from app.auth.users import current_active_user

router = APIRouter()

@router.post("/", response_model=ResponseModel[AssignmentResponse], status_code=status.HTTP_201_CREATED)
async def create_assignment(request: AssignmentCreateRequest,db: Session = Depends(get_db),user: User = Depends(current_active_user),):
    result = mentoring_service.create_assignment_direct(db, user, request)
    return {"success": True, "data": result}

@router.get("/", response_model=ResponseModel[List[AssignmentResponse]])
async def get_assignments(db: Session = Depends(get_db),user: User = Depends(current_active_user),):
    result = mentoring_service.get_all_assignments(db, user)
    return {"success": True, "data": result}

@router.get("/{assignment_id}", response_model=ResponseModel[AssignmentResponse])
async def get_assignment_detail(assignment_id: uuid.UUID,db: Session = Depends(get_db),user: User = Depends(current_active_user),):
    result = mentoring_service.get_assignment_detail(db, user, assignment_id)
    return {"success": True, "data": result}

@router.put("/{assignment_id}", response_model=ResponseModel[AssignmentResponse])
async def update_assignment(assignment_id: uuid.UUID,request: AssignmentUpdateRequest,db: Session = Depends(get_db),user: User = Depends(current_active_user),):
    result = mentoring_service.update_assignment_direct(db, user, assignment_id, request)
    return {"success": True, "data": result}

@router.post("/{assignment_id}/grade", response_model=ResponseModel[AssignmentResponse])
async def grade_assignment(assignment_id: uuid.UUID,request: AssignmentGradeRequest,db: Session = Depends(get_db),user: User = Depends(current_active_user),):
    result = mentoring_service.grade_assignment(db, user, assignment_id, request)
    return {"success": True, "data": result}

@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(assignment_id: uuid.UUID,db: Session = Depends(get_db),user: User = Depends(current_active_user),):
    mentoring_service.delete_assignment_direct(db, user, assignment_id)