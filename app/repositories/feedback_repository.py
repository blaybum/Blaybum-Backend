import uuid
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models.models import MentoringFeedback, Mentoring


class FeedbackRepository(BaseRepository[MentoringFeedback]):
    def __init__(self):
        super().__init__(MentoringFeedback)

    def get_pk_name(self):
        return "feedback_id"

    def get_by_mentoring(
        self, db: Session, mentoring_id: uuid.UUID,
        page: int = 1, limit: int = 10
    ) -> Tuple[List[MentoringFeedback], int]:
        query = db.query(MentoringFeedback).filter(
            MentoringFeedback.mentoring_id == mentoring_id
        )
        total = query.count()
        items = query.order_by(MentoringFeedback.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total


feedback_repo = FeedbackRepository()
