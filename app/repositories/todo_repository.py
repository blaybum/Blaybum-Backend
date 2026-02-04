from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import case, func
from app.models.models import Todo, Planner
from app.repositories.base_repository import BaseRepository
import uuid

class TodoRepository(BaseRepository[Todo]):
    def __init__(self):
        super().__init__(Todo)

    def get_by_id_and_user(self, db: Session, todo_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Todo]:
        return db.query(Todo).join(Planner).filter(
            Todo.todo_id == todo_id,
            Planner.user_id == user_id
        ).first()

    def get_all_by_planner(
        self,
        db: Session,
        planner_id: uuid.UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        sort_by: str = "order_index"
    ) -> List[Todo]:
        query = db.query(Todo).filter(Todo.planner_id == planner_id)

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

        return query.all()

    def get_max_order_index(self, db: Session, planner_id: uuid.UUID) -> int:
        max_order = db.query(func.max(Todo.order_index)).filter(
            Todo.planner_id == planner_id
        ).scalar()
        return max_order or 0

todo_repo = TodoRepository()
