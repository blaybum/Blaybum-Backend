import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.repositories.base_repository import BaseRepository
from app.models.models import Mentoring, MentoringStatus


class MentoringRepository(BaseRepository[Mentoring]):
    def __init__(self):
        super().__init__(Mentoring)

    def get_pk_name(self):
        return "mentoring_id"

    def get_requests_by_mentor(
        self, db: Session, mentor_id: uuid.UUID,
        status_filter: Optional[str] = None,
        page: int = 1, limit: int = 10
    ) -> Tuple[List[Mentoring], int]:
        query = db.query(Mentoring).filter(Mentoring.mentor_id == mentor_id)
        if status_filter:
            query = query.filter(Mentoring.status == status_filter)
        total = query.count()
        items = query.order_by(Mentoring.requested_at.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total

    def get_by_mentor_and_mentee(
        self, db: Session, mentor_id: uuid.UUID, mentee_id: uuid.UUID,
        status_filter: Optional[MentoringStatus] = None
    ) -> Optional[Mentoring]:
        query = db.query(Mentoring).filter(
            Mentoring.mentor_id == mentor_id,
            Mentoring.mentee_id == mentee_id
        )
        if status_filter:
            query = query.filter(Mentoring.status == status_filter)
        return query.first()

    def get_active_by_mentor_and_mentee(
        self, db: Session, mentor_id: uuid.UUID, mentee_id: uuid.UUID
    ) -> Optional[Mentoring]:
        return db.query(Mentoring).filter(
            Mentoring.mentor_id == mentor_id,
            Mentoring.mentee_id == mentee_id,
            Mentoring.status == MentoringStatus.DURING
        ).first()

    def get_mentees_by_mentor(
        self, db: Session, mentor_id: uuid.UUID
    ) -> List[Mentoring]:
        return db.query(Mentoring).filter(
            Mentoring.mentor_id == mentor_id,
            Mentoring.status == MentoringStatus.DURING
        ).all()


mentoring_repo = MentoringRepository()
