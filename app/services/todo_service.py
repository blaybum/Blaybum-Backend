from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories import todo_repo, planner_repo
from app.schemas import TodoCreateRequest, TodoUpdateRequest
from app.models import User, Todo
from fastapi import HTTPException, status
import uuid

class TodoService:
    def create_todo(self, db: Session, user: User, request: TodoCreateRequest):
        planner = planner_repo.get_by_id(db, request.planner_id)
        if not planner or planner.user_id != user.id:
            raise HTTPException(status_code=404, detail="플래너를 찾을 수 없거나 접근 권한이 없습니다.")

        max_order = todo_repo.get_max_order_index(db, request.planner_id)

        new_todo_data = {
            "planner_id": request.planner_id,
            "title": request.title,
            "description": request.description,
            "scheduled_time": request.scheduled_time,
            "estimated_duration_minutes": request.estimated_duration_minutes,
            "priority": request.priority,
            "order_index": max_order + 1
        }
        return todo_repo.create(db, new_todo_data)

    def get_todo(self, db: Session, user: User, todo_id: uuid.UUID):
        todo = todo_repo.get_by_id_and_user(db, todo_id, user.id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="할 일을 찾을 수 없거나 조회 권한이 없습니다."
            )
        return todo

    def get_todos(self, db: Session, user: User, planner_id: uuid.UUID, status_str: str, priority: str, sort_by: str):
        planner = planner_repo.get_by_id(db, planner_id)
        if not planner or planner.user_id != user.id:
            raise HTTPException(status_code=404, detail="플래너를 찾을 수 없거나 접근 권한이 없습니다.")

        return todo_repo.get_all_by_planner(db, planner_id, status_str, priority, sort_by)

    def update_todo(self, db: Session, user: User, todo_id: uuid.UUID, request: TodoUpdateRequest):
        todo = self.get_todo(db, user, todo_id)
        update_data = request.model_dump(exclude_unset=True)
        return todo_repo.update(db, todo, update_data)

    def patch_todo(self, db: Session, user: User, todo_id: uuid.UUID, request: TodoUpdateRequest):
        todo = self.get_todo(db, user, todo_id)
        update_data = request.model_dump(exclude_unset=True)

        if "status" in update_data and update_data["status"] == "completed" and todo.status != "completed":
            todo.completed_at = func.now()
        elif "status" in update_data and update_data["status"] != "completed":
            todo.completed_at = None

        return todo_repo.update(db, todo, update_data)

    def reorder_todos(self, db: Session, user: User, todo_id: uuid.UUID, request: any):
        planner = planner_repo.get_by_id(db, request.planner_id)
        if not planner or planner.user_id != user.id:
            raise HTTPException(status_code=404, detail="플래너를 찾을 수 없거나 접근 권한이 없습니다.")

        try:
            todo_ids = [order.todo_id for order in request.orders]
            order_map = {order.todo_id: order.order_index for order in request.orders}
            
            todos = db.query(Todo).filter(
                Todo.todo_id.in_(todo_ids),
                Todo.planner_id == request.planner_id
            ).all()

            target_todo = None
            for todo in todos:
                todo.order_index = order_map[todo.todo_id]
                db.add(todo)
                if todo.todo_id == todo_id:
                    target_todo = todo
            
            db.commit()
            if target_todo:
                db.refresh(target_todo)
            return target_todo
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"배치 순서 변경 중 오류가 발생했습니다: {str(e)}"
            )

    def reorder_todo(self, db: Session, user: User, todo_id: uuid.UUID, new_order: int):
        todo = self.get_todo(db, user, todo_id)
        return todo_repo.update(db, todo, {"order_index": new_order})

    def delete_todo(self, db: Session, user: User, todo_id: uuid.UUID):
        todo = self.get_todo(db, user, todo_id)
        todo_repo.delete(db, todo)

    def complete_todo(self, db: Session, user: User, todo_id: uuid.UUID, image_data: bytes, mimetype: str):
        todo = self.get_todo(db, user, todo_id)
        
        update_data = {
            "status": "completed",
            "completed_at": func.now(),
            "image_data": image_data,
            "image_mimetype": mimetype
        }
        
        return todo_repo.update(db, todo, update_data)

todo_service = TodoService()
