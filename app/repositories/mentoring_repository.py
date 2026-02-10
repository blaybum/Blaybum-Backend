import uuid
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.repositories.base_repository import BaseRepository
from app.models import (
    Mentoring, Assignment, AssignmentSubmission,
    MentoringQuestion, MentoringFeedback, User, MentoringStatus, AssignmentStatus
)


class MentoringRepository(BaseRepository[Mentoring]):
    def __init__(self):
        super().__init__(Mentoring)

    def get_by_user(self, db: Session, user_id) -> List[Mentoring]:
        return db.query(Mentoring).filter(
            (Mentoring.mentee_id == user_id) | (Mentoring.mentor_id == user_id)
        ).order_by(Mentoring.created_at.desc()).all()

    def get_mentor_requests(self, db: Session, mentor_id) -> List[Mentoring]:
        return db.query(Mentoring).options(
            joinedload(Mentoring.mentee)
        ).filter(
            Mentoring.mentor_id == mentor_id,
            Mentoring.status == MentoringStatus.REQUEST
        ).order_by(Mentoring.requested_at.desc()).all()

    def get_requests_paginated(
        self, db: Session, mentor_id,
        status_filter: Optional[str] = None,
        skip: int = 0, limit: int = 20
    ) -> Tuple[List[Mentoring], int]:
        """API #1: 페이지네이션된 멘토링 신청 목록"""
        query = db.query(Mentoring).filter(Mentoring.mentor_id == mentor_id)
        if status_filter:
            query = query.filter(Mentoring.status == status_filter)
        total = query.count()
        items = (
            query.options(joinedload(Mentoring.mentee))
            .order_by(Mentoring.requested_at.desc())
            .offset(skip).limit(limit).all()
        )
        return items, total

    def get_by_mentor_and_mentee(self, db: Session, mentor_id, mentee_id) -> Optional[Mentoring]:
        return db.query(Mentoring).filter(
            Mentoring.mentor_id == mentor_id,
            Mentoring.mentee_id == mentee_id,
            Mentoring.status.in_([MentoringStatus.DURING, MentoringStatus.REQUEST])
        ).first()

    def get_active_by_mentor_and_mentee(
        self, db: Session, mentor_id, mentee_id
    ) -> Optional[Mentoring]:
        """DURING 상태인 멘토링 관계 조회"""
        return db.query(Mentoring).options(
            joinedload(Mentoring.mentee)
        ).filter(
            Mentoring.mentor_id == mentor_id,
            Mentoring.mentee_id == mentee_id,
            Mentoring.status == MentoringStatus.DURING
        ).first()

    def get_mentoring_ids_for_mentee(
        self, db: Session, mentor_id, mentee_id
    ) -> List[uuid.UUID]:
        """멘토-멘티 관계의 모든 mentoring_id 조회"""
        results = db.query(Mentoring.mentoring_id).filter(
            Mentoring.mentor_id == mentor_id,
            Mentoring.mentee_id == mentee_id
        ).all()
        return [r.mentoring_id for r in results]

    def get_mentee_detail(self, db: Session, mentee_id, mentoring_id):
        return db.query(Mentoring).options(
            joinedload(Mentoring.mentee)
        ).filter(
            Mentoring.mentoring_id == mentoring_id,
            Mentoring.mentee_id == mentee_id
        ).first()

    def get_mentee_statistics(self, db: Session, mentee_id, mentoring_id):
        assignment_stats = db.query(
            func.count(Assignment.assignment_id).label("total_assignments"),
            func.count(func.nullif(Assignment.status == 'GRADED', False)).label("completed_assignments"),
            func.count(func.nullif(Assignment.status == 'ASSIGNED', False)).label("pending_assignments"),
            func.avg(Assignment.grade).label("average_grade")
        ).filter(
            Assignment.mentoring_id == mentoring_id
        ).first()

        question_stats = db.query(
            func.count(MentoringQuestion.question_id).label("total_questions"),
            func.count(func.nullif(MentoringQuestion.is_answered, False)).label("answered_questions")
        ).filter(
            MentoringQuestion.mentoring_id == mentoring_id
        ).first()

        feedback_count = db.query(
            func.count(MentoringFeedback.feedback_id)
        ).filter(
            MentoringFeedback.mentoring_id == mentoring_id
        ).scalar()

        last_activity = db.query(
            func.greatest(
                func.max(Assignment.updated_at),
                func.max(MentoringQuestion.asked_at),
                func.max(MentoringFeedback.created_at)
            )
        ).outerjoin(Assignment, Assignment.mentoring_id == mentoring_id
        ).outerjoin(MentoringQuestion, MentoringQuestion.mentoring_id == mentoring_id
        ).outerjoin(MentoringFeedback, MentoringFeedback.mentoring_id == mentoring_id
        ).scalar()

        return {
            "mentee_id": mentee_id,
            "total_assignments": assignment_stats.total_assignments or 0,
            "completed_assignments": assignment_stats.completed_assignments or 0,
            "pending_assignments": assignment_stats.pending_assignments or 0,
            "average_grade": assignment_stats.average_grade,
            "total_questions": question_stats.total_questions or 0,
            "answered_questions": question_stats.answered_questions or 0,
            "total_feedbacks": feedback_count or 0,
            "last_activity": last_activity
        }

    def get_active_mentoring_by_mentor(self, db: Session, mentor_id) -> Optional[Mentoring]:
        return db.query(Mentoring).filter(
            Mentoring.mentor_id == mentor_id,
            Mentoring.status == MentoringStatus.DURING
        ).first()


class AssignmentRepository(BaseRepository[Assignment]):
    def __init__(self):
        super().__init__(Assignment)

    def get_by_mentoring(self, db: Session, mentoring_id) -> List[Assignment]:
        return db.query(Assignment).filter(
            Assignment.mentoring_id == mentoring_id
        ).order_by(Assignment.created_at.desc()).all()

    def get_by_mentor(self, db: Session, mentor_id) -> List[Assignment]:
        return db.query(Assignment).join(
            Mentoring, Assignment.mentoring_id == Mentoring.mentoring_id
        ).filter(
            Mentoring.mentor_id == mentor_id
        ).order_by(Assignment.created_at.desc()).all()

    def get_paginated(
        self, db: Session, mentoring_id,
        status_filter: Optional[str] = None,
        skip: int = 0, limit: int = 20
    ) -> Tuple[List[Assignment], int]:
        """API #11: 페이지네이션된 과제 목록"""
        query = db.query(Assignment).filter(Assignment.mentoring_id == mentoring_id)
        if status_filter:
            query = query.filter(Assignment.status == status_filter)
        total = query.count()
        items = query.order_by(Assignment.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_by_id_with_submissions(
        self, db: Session, assignment_id
    ) -> Optional[Assignment]:
        """API #12: 과제 상세 (제출물 포함)"""
        return (
            db.query(Assignment)
            .options(joinedload(Assignment.submissions))
            .filter(Assignment.assignment_id == assignment_id)
            .first()
        )

    def get_by_mentoring_ids(
        self, db: Session, mentoring_ids: List[uuid.UUID],
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> List[Assignment]:
        """통계용: 여러 멘토링의 과제 조회"""
        query = db.query(Assignment).filter(Assignment.mentoring_id.in_(mentoring_ids))
        if period_start:
            query = query.filter(Assignment.created_at >= period_start)
        if period_end:
            query = query.filter(Assignment.created_at <= period_end)
        return query.all()


class AssignmentSubmissionRepository(BaseRepository[AssignmentSubmission]):
    def __init__(self):
        super().__init__(AssignmentSubmission)

    def get_by_assignment(self, db: Session, assignment_id) -> List[AssignmentSubmission]:
        return db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id
        ).order_by(AssignmentSubmission.submitted_at.desc()).all()


class QuestionRepository(BaseRepository[MentoringQuestion]):
    def __init__(self):
        super().__init__(MentoringQuestion)

    def get_by_mentoring(self, db: Session, mentoring_id) -> List[MentoringQuestion]:
        return db.query(MentoringQuestion).filter(
            MentoringQuestion.mentoring_id == mentoring_id
        ).order_by(MentoringQuestion.asked_at.desc()).all()

    def get_by_mentor(self, db: Session, mentor_id) -> List[MentoringQuestion]:
        return db.query(MentoringQuestion).join(
            Mentoring, MentoringQuestion.mentoring_id == Mentoring.mentoring_id
        ).filter(
            Mentoring.mentor_id == mentor_id
        ).order_by(MentoringQuestion.asked_at.desc()).all()

    def get_paginated(
        self, db: Session, mentoring_id,
        is_answered: Optional[bool] = None,
        skip: int = 0, limit: int = 20
    ) -> Tuple[List[MentoringQuestion], int]:
        """API #16: 페이지네이션된 질문 목록"""
        query = db.query(MentoringQuestion).filter(
            MentoringQuestion.mentoring_id == mentoring_id
        )
        if is_answered is not None:
            query = query.filter(MentoringQuestion.is_answered == is_answered)
        total = query.count()
        items = query.order_by(MentoringQuestion.asked_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_by_mentoring_ids(
        self, db: Session, mentoring_ids: List[uuid.UUID],
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> List[MentoringQuestion]:
        """통계용"""
        query = db.query(MentoringQuestion).filter(
            MentoringQuestion.mentoring_id.in_(mentoring_ids)
        )
        if period_start:
            query = query.filter(MentoringQuestion.asked_at >= period_start)
        if period_end:
            query = query.filter(MentoringQuestion.asked_at <= period_end)
        return query.all()


class FeedbackRepository(BaseRepository[MentoringFeedback]):
    def __init__(self):
        super().__init__(MentoringFeedback)

    def get_by_mentoring(self, db: Session, mentoring_id) -> List[MentoringFeedback]:
        return db.query(MentoringFeedback).filter(
            MentoringFeedback.mentoring_id == mentoring_id
        ).order_by(MentoringFeedback.created_at.desc()).all()

    def get_paginated_by_mentoring_ids(
        self, db: Session, mentoring_ids: List[uuid.UUID],
        skip: int = 0, limit: int = 20
    ) -> Tuple[List[MentoringFeedback], int]:
        """API #9: 페이지네이션된 피드백 목록"""
        query = db.query(MentoringFeedback).filter(
            MentoringFeedback.mentoring_id.in_(mentoring_ids)
        )
        total = query.count()
        items = query.order_by(MentoringFeedback.created_at.desc()).offset(skip).limit(limit).all()
        return items, total


mentoring_repo = MentoringRepository()
assignment_repo = AssignmentRepository()
submission_repo = AssignmentSubmissionRepository()
question_repo = QuestionRepository()
feedback_repo = FeedbackRepository()
