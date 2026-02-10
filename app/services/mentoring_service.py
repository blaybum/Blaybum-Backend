import uuid
import math
from datetime import datetime, timedelta, date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.repositories import mentoring_repo, assignment_repo, question_repo, feedback_repo
from app.models.models import (
    User, Mentoring, MentoringStatus, Assignment, AssignmentStatus,
    MentoringQuestion, MentoringFeedback, Todo, TodoStatus, Pomo, Planner
)
from app.schemas.mentoring_schemas import (
    MentoringAcceptRequest, MentoringRejectRequest, MentoringStatusUpdateRequest,
    AssignmentCreateRequest, AssignmentUpdateRequest, AssignmentGradeRequest,
    QuestionAnswerRequest, FeedbackCreateRequest,
)


class MentoringService:

    # ===== 멘토링 신청 관리 =====

    def get_mentoring_requests(
        self, db: Session, user: User,
        page: int = 1, limit: int = 10,
        status_filter: Optional[str] = None
    ):
        items, total = mentoring_repo.get_requests_by_mentor(
            db, user.id, status_filter=status_filter, page=page, limit=limit
        )

        requests = []
        for m in items:
            requests.append({
                "mentoring_id": m.mentoring_id,
                "mentee_id": m.mentee_id,
                "mentee_name": m.mentee.full_name if m.mentee else None,
                "mentee_email": m.mentee.email if m.mentee else None,
                "requested_at": m.requested_at,
                "status": m.status.value if m.status else None,
            })

        total_pages = math.ceil(total / limit) if limit > 0 else 0
        return {
            "requests": requests,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total,
                "items_per_page": limit,
            }
        }

    def accept_request(
        self, db: Session, user: User,
        mentoring_id: uuid.UUID, request: MentoringAcceptRequest
    ):
        mentoring = mentoring_repo.get_by_id(db, mentoring_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="멘토링 신청을 찾을 수 없습니다.")
        if mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        if mentoring.status != MentoringStatus.REQUEST:
            raise HTTPException(status_code=400, detail="이미 처리된 신청입니다.")

        now = datetime.now()
        mentoring_repo.update(db, mentoring, {
            "status": MentoringStatus.DURING,
            "started_at": now,
        })

        return {
            "mentoring_id": mentoring.mentoring_id,
            "status": mentoring.status.value,
            "started_at": mentoring.started_at,
        }

    def reject_request(
        self, db: Session, user: User,
        mentoring_id: uuid.UUID, request: MentoringRejectRequest
    ):
        mentoring = mentoring_repo.get_by_id(db, mentoring_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="멘토링 신청을 찾을 수 없습니다.")
        if mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        if mentoring.status != MentoringStatus.REQUEST:
            raise HTTPException(status_code=400, detail="이미 처리된 신청입니다.")

        mentoring_repo.delete(db, mentoring)
        return {"message": "멘토링 신청이 거절되었습니다."}

    # ===== 멘토링 상태 관리 =====

    def update_status(
        self, db: Session, user: User,
        mentoring_id: uuid.UUID, request: MentoringStatusUpdateRequest
    ):
        mentoring = mentoring_repo.get_by_id(db, mentoring_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="멘토링을 찾을 수 없습니다.")
        if mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        new_status = request.status
        if new_status not in ("DURING", "END"):
            raise HTTPException(status_code=400, detail="잘못된 status 값입니다.")

        update_data = {"status": MentoringStatus(new_status)}
        if new_status == "END":
            update_data["ended_at"] = datetime.now()

        mentoring_repo.update(db, mentoring, update_data)

        return {
            "mentoring_id": mentoring.mentoring_id,
            "status": mentoring.status.value,
            "ended_at": mentoring.ended_at,
        }

    def delete_mentoring(self, db: Session, user: User, mentoring_id: uuid.UUID):
        mentoring = mentoring_repo.get_by_id(db, mentoring_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="멘토링을 찾을 수 없습니다.")
        if mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        mentoring_repo.delete(db, mentoring)
        return {"message": "멘토링이 종료되었습니다."}

    # ===== 멘티 정보 =====

    def get_mentee_detail(self, db: Session, user: User, mentee_id: uuid.UUID):
        mentoring = mentoring_repo.get_active_by_mentor_and_mentee(db, user.id, mentee_id)
        if not mentoring:
            mentoring = mentoring_repo.get_by_mentor_and_mentee(db, user.id, mentee_id)
            if not mentoring:
                raise HTTPException(status_code=404, detail="멘티를 찾을 수 없습니다.")
            if mentoring.mentor_id != user.id:
                raise HTTPException(status_code=403, detail="멘토링 관계가 아닙니다.")

        mentee = mentoring.mentee

        # 완료된 todo 수
        completed_todos = db.query(func.count(Todo.todo_id)).join(
            Planner, Todo.planner_id == Planner.planner_id
        ).filter(
            Planner.user_id == mentee_id,
            Todo.status == TodoStatus.completed
        ).scalar() or 0

        # 대기 중인 과제 수
        pending_assignments = assignment_repo.count_pending_by_mentoring(db, mentoring.mentoring_id)

        # 총 공부 시간 (분)
        total_study_time = db.query(
            func.sum(
                func.extract('epoch', Pomo.real_end_time - Pomo.real_start_time) / 60
            )
        ).filter(Pomo.user_id == mentee_id).scalar() or 0

        return {
            "mentee_id": mentee.id,
            "name": mentee.full_name,
            "email": mentee.email,
            "profile_image": mentee.profile_image,
            "mentoring_id": mentoring.mentoring_id,
            "mentoring_status": mentoring.status.value,
            "started_at": mentoring.started_at,
            "total_study_time": int(total_study_time),
            "recent_activity": {
                "last_login": None,
                "completed_todos": completed_todos,
                "pending_assignments": pending_assignments,
            }
        }

    # ===== 과제 관리 =====

    def get_assignments(
        self, db: Session, user: User,
        mentoring_id: Optional[uuid.UUID] = None,
        status_filter: Optional[str] = None,
        page: int = 1, limit: int = 10
    ):
        items, total = assignment_repo.get_by_mentor(
            db, user.id, mentoring_id=mentoring_id,
            status_filter=status_filter, page=page, limit=limit
        )

        assignments = []
        for a in items:
            mentee_name = None
            if a.mentoring and a.mentoring.mentee:
                mentee_name = a.mentoring.mentee.full_name
            assignments.append({
                "assignment_id": a.assignment_id,
                "mentoring_id": a.mentoring_id,
                "mentee_name": mentee_name,
                "title": a.title,
                "due_date": a.due_date,
                "status": a.status.value if a.status else None,
                "created_at": a.created_at,
            })

        total_pages = math.ceil(total / limit) if limit > 0 else 0
        return {
            "assignments": assignments,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total,
            }
        }

    def get_assignment_detail(self, db: Session, user: User, assignment_id: uuid.UUID):
        assignment = assignment_repo.get_by_id(db, assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
        if assignment.mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        mentee = assignment.mentoring.mentee
        submission_data = None
        if assignment.submission:
            s = assignment.submission
            submission_data = {
                "submission_id": s.submission_id,
                "content": s.content,
                "file_url": s.file_url,
                "submitted_at": s.submitted_at,
            }

        return {
            "assignment_id": assignment.assignment_id,
            "mentoring_id": assignment.mentoring_id,
            "mentee_id": mentee.id if mentee else None,
            "mentee_name": mentee.full_name if mentee else None,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date,
            "status": assignment.status.value if assignment.status else None,
            "grade": assignment.grade,
            "created_at": assignment.created_at,
            "submission": submission_data,
        }

    def create_assignment(self, db: Session, user: User, request: AssignmentCreateRequest):
        mentoring = mentoring_repo.get_by_id(db, request.mentoring_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="멘토링을 찾을 수 없습니다.")
        if mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        assignment_data = {
            "mentoring_id": request.mentoring_id,
            "title": request.title,
            "description": request.description,
            "due_date": request.due_date,
            "status": AssignmentStatus.ASSIGNED,
        }
        assignment = assignment_repo.create(db, assignment_data)

        return {
            "assignment_id": assignment.assignment_id,
            "mentoring_id": assignment.mentoring_id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date,
            "status": assignment.status.value,
            "created_at": assignment.created_at,
        }

    def update_assignment(
        self, db: Session, user: User,
        assignment_id: uuid.UUID, request: AssignmentUpdateRequest
    ):
        assignment = assignment_repo.get_by_id(db, assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
        if assignment.mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        update_data = request.model_dump(exclude_unset=True)
        assignment = assignment_repo.update(db, assignment, update_data)

        return {
            "assignment_id": assignment.assignment_id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date,
            "updated_at": assignment.updated_at,
        }

    def delete_assignment(self, db: Session, user: User, assignment_id: uuid.UUID):
        assignment = assignment_repo.get_by_id(db, assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
        if assignment.mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        assignment_repo.delete(db, assignment)
        return {"message": "과제가 삭제되었습니다."}

    def grade_assignment(
        self, db: Session, user: User,
        assignment_id: uuid.UUID, request: AssignmentGradeRequest
    ):
        assignment = assignment_repo.get_by_id(db, assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
        if assignment.mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        if assignment.status != AssignmentStatus.SUBMITTED:
            raise HTTPException(status_code=400, detail="제출되지 않은 과제입니다.")

        assignment_repo.update(db, assignment, {
            "grade": request.grade,
            "comment": request.comment,
            "status": AssignmentStatus.GRADED,
        })

        return {
            "assignment_id": assignment.assignment_id,
            "grade": assignment.grade,
            "status": assignment.status.value,
            "comment": assignment.comment,
        }

    # ===== 질문 관리 =====

    def get_questions(
        self, db: Session, user: User,
        mentoring_id: Optional[uuid.UUID] = None,
        is_answered: Optional[bool] = None,
        page: int = 1, limit: int = 10
    ):
        items, total = question_repo.get_by_mentor(
            db, user.id, mentoring_id=mentoring_id,
            is_answered=is_answered, page=page, limit=limit
        )

        questions = []
        for q in items:
            mentee_name = None
            if q.mentoring and q.mentoring.mentee:
                mentee_name = q.mentoring.mentee.full_name
            questions.append({
                "question_id": q.question_id,
                "mentoring_id": q.mentoring_id,
                "mentee_name": mentee_name,
                "question": q.question,
                "is_answered": q.is_answered,
                "asked_at": q.asked_at,
            })

        total_pages = math.ceil(total / limit) if limit > 0 else 0
        return {
            "questions": questions,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total,
            }
        }

    def answer_question(
        self, db: Session, user: User,
        question_id: uuid.UUID, request: QuestionAnswerRequest
    ):
        question = question_repo.get_by_id(db, question_id)
        if not question:
            raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
        if question.mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        now = datetime.now()
        question_repo.update(db, question, {
            "answer": request.answer,
            "is_answered": True,
            "answered_at": now,
        })

        return {
            "question_id": question.question_id,
            "question": question.question,
            "answer": question.answer,
            "is_answered": question.is_answered,
            "answered_at": question.answered_at,
        }

    # ===== 피드백 관리 =====

    def get_feedbacks(
        self, db: Session, user: User, mentee_id: uuid.UUID,
        page: int = 1, limit: int = 10
    ):
        mentoring = mentoring_repo.get_by_mentor_and_mentee(db, user.id, mentee_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="멘티를 찾을 수 없습니다.")
        if mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        items, total = feedback_repo.get_by_mentoring(
            db, mentoring.mentoring_id, page=page, limit=limit
        )

        feedbacks = []
        for f in items:
            feedbacks.append({
                "feedback_id": f.feedback_id,
                "content": f.content,
                "created_at": f.created_at,
            })

        total_pages = math.ceil(total / limit) if limit > 0 else 0
        return {
            "feedbacks": feedbacks,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total,
            }
        }

    def create_feedback(
        self, db: Session, user: User,
        mentee_id: uuid.UUID, request: FeedbackCreateRequest
    ):
        mentoring = mentoring_repo.get_active_by_mentor_and_mentee(db, user.id, mentee_id)
        if not mentoring:
            mentoring = mentoring_repo.get_by_mentor_and_mentee(db, user.id, mentee_id)
            if not mentoring:
                raise HTTPException(status_code=404, detail="멘티를 찾을 수 없습니다.")
            if mentoring.mentor_id != user.id:
                raise HTTPException(status_code=403, detail="멘토링 관계가 아닙니다.")

        feedback_data = {
            "mentoring_id": mentoring.mentoring_id,
            "content": request.content,
        }
        feedback = feedback_repo.create(db, feedback_data)

        return {
            "feedback_id": feedback.feedback_id,
            "mentoring_id": feedback.mentoring_id,
            "content": feedback.content,
            "created_at": feedback.created_at,
        }

    # ===== 멘티 학습 통계 =====

    def get_mentee_statistics(
        self, db: Session, user: User,
        mentee_id: uuid.UUID, period: str = "week"
    ):
        mentoring = mentoring_repo.get_by_mentor_and_mentee(db, user.id, mentee_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="멘티를 찾을 수 없습니다.")
        if mentoring.mentor_id != user.id:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        # 기간 계산
        today = date.today()
        if period == "week":
            start_date = today - timedelta(days=7)
        elif period == "month":
            start_date = today - timedelta(days=30)
        else:
            start_date = None

        # 일별 공부 시간
        pomo_query = db.query(
            func.date(Pomo.real_start_time).label("study_date"),
            func.sum(
                func.extract('epoch', Pomo.real_end_time - Pomo.real_start_time) / 60
            ).label("minutes")
        ).filter(Pomo.user_id == mentee_id)

        if start_date:
            pomo_query = pomo_query.filter(func.date(Pomo.real_start_time) >= start_date)

        pomo_query = pomo_query.group_by(func.date(Pomo.real_start_time)).order_by(func.date(Pomo.real_start_time))
        daily_study = pomo_query.all()

        daily_study_time = [
            {"date": str(row.study_date), "minutes": int(row.minutes or 0)}
            for row in daily_study
        ]
        total_study_time = sum(d["minutes"] for d in daily_study_time)

        # 과제 통계
        assignments = assignment_repo.get_by_mentoring(db, mentoring.mentoring_id)
        total_assignments = len(assignments)
        completed_assignments = sum(1 for a in assignments if a.status == AssignmentStatus.GRADED)
        pending_count = sum(1 for a in assignments if a.status == AssignmentStatus.ASSIGNED)
        graded = [a.grade for a in assignments if a.grade is not None]
        average_grade = round(sum(graded) / len(graded), 1) if graded else None

        # Todo 통계
        todo_query = db.query(Todo).join(Planner).filter(Planner.user_id == mentee_id)
        if start_date:
            todo_query = todo_query.filter(Planner.plan_date >= start_date)
        all_todos = todo_query.all()
        total_todos = len(all_todos)
        completed_todos = sum(1 for t in all_todos if t.status == TodoStatus.completed)
        completion_rate = round((completed_todos / total_todos) * 100, 1) if total_todos > 0 else 0

        return {
            "period": period,
            "total_study_time": total_study_time,
            "daily_study_time": daily_study_time,
            "assignments": {
                "total": total_assignments,
                "completed": completed_assignments,
                "pending": pending_count,
                "average_grade": average_grade,
            },
            "todos": {
                "total": total_todos,
                "completed": completed_todos,
                "completion_rate": completion_rate,
            }
        }


mentoring_service = MentoringService()
