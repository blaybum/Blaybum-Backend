import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import TodoCreateRequest, ResponseModel, TodoResponse, TodoUpdateRequest
from app.models.models import User
from app.services.todo_service import todo_service
from app.auth.users import current_active_user

router = APIRouter()

@router.post("/", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_201_CREATED)
async def create_todo(
    request: TodoCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = todo_service.create_todo(db, user, request)
    return {"success": True, "data": result}

@router.get("/", response_model=ResponseModel[List[TodoResponse]])
async def get_todos(
    planner_id: uuid.UUID,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: str = "order_index",
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = todo_service.get_todos(db, user, planner_id, status, priority, sort_by)
    return {"success": True, "data": result}

@router.get("/{todo_id}", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_200_OK)
async def get_todo(
    todo_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = todo_service.get_todo(db, user, todo_id)
    return {"success": True, "data": result}

@router.put("/{todo_id}", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_200_OK)
async def update_todo(
    todo_id: uuid.UUID,
    request: TodoUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = todo_service.update_todo(db, user, todo_id, request)
    return {"success": True, "data": result}

@router.patch("/{todo_id}", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_200_OK)
async def patch_todo(
    todo_id: uuid.UUID,
    request: TodoUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = todo_service.patch_todo(db, user, todo_id, request)
    return {"success": True, "data": result}

@router.patch("/{todo_id}/reorder", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_200_OK)
async def reorder_todos(
    todo_id: uuid.UUID,
    request: TodoReorderRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = todo_service.reorder_todos(db, user, todo_id, request)
    return {"success": True, "data": result}

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    todo_service.delete_todo(db, user, todo_id)
    return