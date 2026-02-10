import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models.models import Assignment, Mentoring


class AssignmentRepository(BaseRepository[Assignment]):
    def __init__(self):
        super().__init__(Assignment)

    def get_pk_name(self):
        return "assignment_id"

    def get_by_mentor(
        self, db: Session, mentor_id: uuid.UUID,
        mentoring_id: Optional[uuid.UUID] = None,
        status_filter: Optional[str] = None,
        page: int = 1, limit: int = 10
    ) -> Tuple[List[Assignment], int]:
        query = db.query(Assignment).join(Mentoring).filter(Mentoring.mentor_id == mentor_id)
        if mentoring_id:
            query = query.filter(Assignment.mentoring_id == mentoring_id)
        if status_filter:
            query = query.filter(Assignment.status == status_filter)
        total = query.count()
        items = query.order_by(Assignment.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total

    def get_by_mentoring(
        self, db: Session, mentoring_id: uuid.UUID
    ) -> List[Assignment]:
        return db.query(Assignment).filter(
            Assignment.mentoring_id == mentoring_id
        ).all()

    def count_pending_by_mentoring(
        self, db: Session, mentoring_id: uuid.UUID
    ) -> int:
        return db.query(Assignment).filter(
            Assignment.mentoring_id == mentoring_id,
            Assignment.status == "ASSIGNED"
        ).count()


assignment_repo = AssignmentRepository()
