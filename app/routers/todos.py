import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import case, func

from app.database import get_db
from app.schemas.schemas import TodoCreateRequest, ResponseModel, TodoResponse, TodoUpdateRequest
from app.models.models import Todo, User, Planner

router = APIRouter()

@router.post("/", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_201_CREATED)
async def create_todo(request: TodoCreateRequest, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    new_todo = Todo(
        user_id=user.id,
        planner_id=request.planner_id,
        title=request.title,
        description=request.description,
        scheduled_time=request.scheduled_time,
        estimated_duration_minutes=request.estimated_duration_minutes,
        priority=request.priority
    )

    try:
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        return {
            "success": True,
            "data": new_todo
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"할 일 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.put("/{todo_id}", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_200_OK)
async def update_todo(todo_id: uuid.UUID, request: TodoUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다.")

    todo.title = request.title
    todo.description = request.description
    todo.scheduled_time = request.scheduled_time
    todo.estimated_duration_minutes = request.estimated_duration_minutes
    todo.priority = request.priority
    todo.is_completed = request.is_completed

    try:
        db.commit()
        db.refresh(todo)
        return {
            "success": True,
            "data": todo
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"할 일 수정 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/", response_model=ResponseModel[List[TodoResponse]])
async def get_todos(
    planner_id: uuid.UUID,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: str = "order_index",
    db: Session = Depends(get_db)
):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    query = db.query(Todo).join(Planner).filter(
        Planner.user_id == user.id,
        Todo.planner_id == planner_id
    )

    if status:
        query = query.filter(Todo.status == status)
    if priority:
        query = query.filter(Todo.priority == priority)

    if sort_by == "priority":
        p_order = case(
            { "high": 1, "medium": 2, "low": 3 },
            value=Todo.priority
        )
        query = query.order_by(p_order)
    elif sort_by == "scheduled_time":
        query = query.order_by(Todo.scheduled_time.asc())
    else:
        query = query.order_by(Todo.order_index.asc())

    todos = query.all()

    return {
        "success": True,
        "data": todos
    }

@router.patch("/{todo_id}/reorder", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_200_OK)
async def reorder_todos(todo_id: uuid.UUID, request: TodoUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    todo = db.query(Todo).filter(Todo.todo_id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다.")

    todo.order_index = request.order_index

    try:
        db.commit()
        db.refresh(todo)
        return {
            "success": True,
            "data": todo
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"할 일 순서 변경 중 오류가 발생했습니다: {str(e)}"
        )

@router.patch("/{todo_id}", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_200_OK)
async def patch_todo(todo_id: uuid.UUID, request: TodoUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    todo_query = db.query(Todo).join(Planner).filter(
        Todo.todo_id == todo_id,
        Planner.user_id == user.id
    )
    
    db_todo = todo_query.first()
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="할 일을 찾을 수 없거나 수정 권한이 없습니다."
        )

    update_data = request.dict(exclude_unset=True)
    
    if "status" in update_data and update_data["status"] == "completed" and db_todo.status != "completed":
        db_todo.completed_at = func.now()
    elif "status" in update_data and update_data["status"] != "completed":
        db_todo.completed_at = None

    try:
        for key, value in update_data.items():
            setattr(db_todo, key, value)
        
        db.commit()
        db.refresh(db_todo)

        return {
            "success": True,
            "data": db_todo
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"업데이트 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/{todo_id}", response_model=ResponseModel[TodoResponse], status_code=status.HTTP_200_OK)
async def get_todo(todo_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    todo = db.query(Todo).join(Planner).filter(
        Todo.todo_id == todo_id,
        Planner.user_id == user.id
    ).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="할 일을 찾을 수 없거나 조회 권한이 없습니다."
        )

    return {
        "success": True,
        "data": todo
    }

@router.delete("/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(todo_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    todo_query = db.query(Todo).join(Planner).filter(
        Todo.todo_id == todo_id,
        Planner.user_id == user.id
    )
    
    db_todo = todo_query.first()
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="할 일을 찾을 수 없거나 삭제 권한이 없습니다."
        )

    try:
        db.delete(db_todo)
        db.commit()
        return {
            "success": True,
            "data": db_todo
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"삭제 중 오류가 발생했습니다: {str(e)}"
        )