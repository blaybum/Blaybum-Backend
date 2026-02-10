import uuid
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models import User, MentorMentee
from app.repositories.mentoring_repository import mentoring_repo


class MentoringService:
    def get_mentees(
        self,
        db: Session,
        mentor: User,
        page: int,
        limit: int,
    ) -> Tuple[List[MentorMentee], int]:
        skip = (page - 1) * limit
        return mentoring_repo.get_mentees_by_mentor(db, mentor.id, skip, limit)


mentoring_service = MentoringService()
