import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models.models import MentoringQuestion, Mentoring


class QuestionRepository(BaseRepository[MentoringQuestion]):
    def __init__(self):
        super().__init__(MentoringQuestion)

    def get_pk_name(self):
        return "question_id"

    def get_by_mentor(
        self, db: Session, mentor_id: uuid.UUID,
        mentoring_id: Optional[uuid.UUID] = None,
        is_answered: Optional[bool] = None,
        page: int = 1, limit: int = 10
    ) -> Tuple[List[MentoringQuestion], int]:
        query = db.query(MentoringQuestion).join(Mentoring).filter(Mentoring.mentor_id == mentor_id)
        if mentoring_id:
            query = query.filter(MentoringQuestion.mentoring_id == mentoring_id)
        if is_answered is not None:
            query = query.filter(MentoringQuestion.is_answered == is_answered)
        total = query.count()
        items = query.order_by(MentoringQuestion.asked_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total


question_repo = QuestionRepository()
