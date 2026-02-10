import uuid
from typing import List, Tuple, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import MentorMentee


class MentoringRepository:
    def get_mentees_by_mentor(
        self,
        db: Session,
        mentor_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[MentorMentee], int]:
        query = (
            db.query(MentorMentee)
            .options(joinedload(MentorMentee.mentee))
            .filter(MentorMentee.mentor_id == mentor_id)
        )
        total_items = query.count()
        results = query.order_by(MentorMentee.created_at.desc()).offset(skip).limit(limit).all()
        return results, total_items

    def get_by_mentor_and_mentee(
        self, db: Session, mentor_id: uuid.UUID, mentee_id: uuid.UUID
    ) -> Optional[MentorMentee]:
        return (
            db.query(MentorMentee)
            .filter(
                MentorMentee.mentor_id == mentor_id,
                MentorMentee.mentee_id == mentee_id,
            )
            .first()
        )


mentoring_repo = MentoringRepository()
