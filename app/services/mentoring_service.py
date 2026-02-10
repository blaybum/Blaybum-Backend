import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import User, MentoringStatus, AssignmentStatus
from app.repositories.mentoring_repository import (
    mentoring_repo, assignment_repo, submission_repo,
    question_repo, feedback_repo
)
from app.schemas.mentoring_schemas import (
    MentoringCreateRequest, MentoringStatusUpdateRequest,
    AssignmentCreateRequest, AssignmentUpdateRequest,
    SubmissionCreateRequest,
    QuestionCreateRequest, QuestionAnswerRequest,
    FeedbackCreateRequest, AssignmentGradeRequest
)

class MentoringService:

    def _get_mentoring_or_404(self, db: Session, mentoring_id: uuid.UUID):
        mentoring = mentoring_repo.get_by_id(db, mentoring_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="멘토링을 찾을 수 없습니다.")
        return mentoring

    def _check_mentoring_member(self, mentoring, user: User):
        if user.id not in (mentoring.mentee_id, mentoring.mentor_id):
            raise HTTPException(status_code=403, detail="해당 멘토링에 대한 권한이 없습니다.")

    def create_mentoring_request(self, db: Session, user: User, request: MentoringCreateRequest):
        if user.id == request.mentor_id:
            raise HTTPException(status_code=400, detail="자기 자신에게 멘토링을 요청할 수 없습니다.")
        return mentoring_repo.create(db, {
            "mentee_id": user.id,
            "mentor_id": request.mentor_id,
        })

    def create_mentoring(self, db: Session, user: User, request: MentoringCreateRequest):
        return self.create_mentoring_request(db, user, request)

    def get_my_mentorings(self, db: Session, user: User):
        return mentoring_repo.get_by_user(db, user.id)

    def get_mentoring(self, db: Session, user: User, mentoring_id: uuid.UUID):
        mentoring = self._get_mentoring_or_404(db, mentoring_id)
        self._check_mentoring_member(mentoring, user)
        return mentoring

    def update_mentoring_status(self, db: Session, user: User, mentoring_id: uuid.UUID, request: MentoringStatusUpdateRequest):
        mentoring = self._get_mentoring_or_404(db, mentoring_id)
        self._check_mentoring_member(mentoring, user)

        update_data = {"status": request.status}
        now = datetime.utcnow()
        if request.status == MentoringStatus.DURING:
            update_data["started_at"] = now
        elif request.status == MentoringStatus.END:
            update_data["ended_at"] = now

        return mentoring_repo.update(db, mentoring, update_data)

    def delete_mentoring(self, db: Session, user: User, mentoring_id: uuid.UUID):
        mentoring = self._get_mentoring_or_404(db, mentoring_id)
        self._check_mentoring_member(mentoring, user)
        mentoring_repo.delete(db, mentoring)

    def create_assignment(self, db: Session, user: User, mentoring_id: uuid.UUID, request: AssignmentCreateRequest):
        mentoring = self.get_mentoring(db, user, mentoring_id)
        if user.id != mentoring.mentor_id:
            raise HTTPException(status_code=403, detail="멘토만 과제를 생성할 수 있습니다.")
        return assignment_repo.create(db, {
            "mentoring_id": mentoring_id,
            "title": request.title,
            "description": request.description,
            "due_date": request.due_date,
        })

    def get_assignments(self, db: Session, user: User, mentoring_id: uuid.UUID):
        self.get_mentoring(db, user, mentoring_id)
        return assignment_repo.get_by_mentoring(db, mentoring_id)

    def get_assignment(self, db: Session, user: User, mentoring_id: uuid.UUID, assignment_id: uuid.UUID):
        self.get_mentoring(db, user, mentoring_id)
        assignment = assignment_repo.get_by_id(db, assignment_id)
        if not assignment or assignment.mentoring_id != mentoring_id:
            raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
        return assignment

    def update_assignment(self, db: Session, user: User, mentoring_id: uuid.UUID, assignment_id: uuid.UUID, request: AssignmentUpdateRequest):
        assignment = self.get_assignment(db, user, mentoring_id, assignment_id)
        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 데이터가 없습니다.")
        return assignment_repo.update(db, assignment, update_data)

    def delete_assignment(self, db: Session, user: User, mentoring_id: uuid.UUID, assignment_id: uuid.UUID):
        assignment = self.get_assignment(db, user, mentoring_id, assignment_id)
        assignment_repo.delete(db, assignment)

    def create_submission(self, db: Session, user: User, mentoring_id: uuid.UUID, assignment_id: uuid.UUID, request: SubmissionCreateRequest):
        mentoring = self.get_mentoring(db, user, mentoring_id)
        if user.id != mentoring.mentee_id:
            raise HTTPException(status_code=403, detail="멘티만 과제를 제출할 수 있습니다.")
        self.get_assignment(db, user, mentoring_id, assignment_id)
        return submission_repo.create(db, {
            "assignment_id": assignment_id,
            "content": request.content,
            "file_url": request.file_url,
        })

    def get_submissions(self, db: Session, user: User, mentoring_id: uuid.UUID, assignment_id: uuid.UUID):
        self.get_assignment(db, user, mentoring_id, assignment_id)
        return submission_repo.get_by_assignment(db, assignment_id)

    def create_question(self, db: Session, user: User, mentoring_id: uuid.UUID, request: QuestionCreateRequest):
        mentoring = self.get_mentoring(db, user, mentoring_id)
        if user.id != mentoring.mentee_id:
            raise HTTPException(status_code=403, detail="멘티만 질문을 생성할 수 있습니다.")
        return question_repo.create(db, {
            "mentoring_id": mentoring_id,
            "question": request.question,
        })

    def get_questions(self, db: Session, user: User, mentoring_id: uuid.UUID):
        self.get_mentoring(db, user, mentoring_id)
        return question_repo.get_by_mentoring(db, mentoring_id)

    def answer_question(self, db: Session, user: User, mentoring_id: uuid.UUID, question_id: uuid.UUID, request: QuestionAnswerRequest):
        mentoring = self.get_mentoring(db, user, mentoring_id)
        if user.id != mentoring.mentor_id:
            raise HTTPException(status_code=403, detail="멘토만 답변할 수 있습니다.")
        question = question_repo.get_by_id(db, question_id)
        if not question or question.mentoring_id != mentoring_id:
            raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
        return question_repo.update(db, question, {
            "answer": request.answer,
            "is_answered": True,
            "answered_at": datetime.utcnow(),
        })

    def delete_question(self, db: Session, user: User, mentoring_id: uuid.UUID, question_id: uuid.UUID):
        self.get_mentoring(db, user, mentoring_id)
        question = question_repo.get_by_id(db, question_id)
        if not question or question.mentoring_id != mentoring_id:
            raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
        question_repo.delete(db, question)

    def create_feedback(self, db: Session, user: User, mentoring_id: uuid.UUID, request: FeedbackCreateRequest):
        mentoring = self.get_mentoring(db, user, mentoring_id)
        if user.id != mentoring.mentor_id:
            raise HTTPException(status_code=403, detail="멘토만 피드백을 작성할 수 있습니다.")
        return feedback_repo.create(db, {
            "mentoring_id": mentoring_id,
            "content": request.content,
        })

    def get_feedbacks(self, db: Session, user: User, mentoring_id: uuid.UUID):
        self.get_mentoring(db, user, mentoring_id)
        return feedback_repo.get_by_mentoring(db, mentoring_id)

    def delete_feedback(self, db: Session, user: User, mentoring_id: uuid.UUID, feedback_id: uuid.UUID):
        self.get_mentoring(db, user, mentoring_id)
        feedback = feedback_repo.get_by_id(db, feedback_id)
        if not feedback or feedback.mentoring_id != mentoring_id:
            raise HTTPException(status_code=404, detail="피드백을 찾을 수 없습니다.")
        feedback_repo.delete(db, feedback)

    def get_mentoring_requests(self, db: Session, user: User):
        return mentoring_repo.get_mentor_requests(db, user.id)

    def accept_mentoring_request(self, db: Session, user: User, mentoring_id: uuid.UUID):
        mentoring = self._get_mentoring_or_404(db, mentoring_id)
        if user.id != mentoring.mentor_id:
            raise HTTPException(status_code=403, detail="멘토만 멘토링 신청을 수락할 수 있습니다.")
        if mentoring.status != MentoringStatus.REQUEST:
            raise HTTPException(status_code=400, detail="이미 처리된 멘토링 신청입니다.")
        
        update_data = {
            "status": MentoringStatus.DURING,
            "started_at": datetime.utcnow()
        }
        return mentoring_repo.update(db, mentoring, update_data)

    def reject_mentoring_request(self, db: Session, user: User, mentoring_id: uuid.UUID):
        mentoring = self._get_mentoring_or_404(db, mentoring_id)
        if user.id != mentoring.mentor_id:
            raise HTTPException(status_code=403, detail="멘토만 멘토링 신청을 거절할 수 있습니다.")
        if mentoring.status != MentoringStatus.REQUEST:
            raise HTTPException(status_code=400, detail="이미 처리된 멘토링 신청입니다.")
        
        mentoring_repo.delete(db, mentoring)
        return mentoring

    def get_mentee_detail(self, db: Session, user: User, mentee_id: uuid.UUID):
        mentoring = mentoring_repo.get_by_mentor_and_mentee(db, user.id, mentee_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="해당 멘티와의 멘토링을 찾을 수 없습니다.")
        return mentoring_repo.get_mentee_detail(db, mentee_id, mentoring.mentoring_id)

    def get_mentee_statistics(self, db: Session, user: User, mentee_id: uuid.UUID):
        mentoring = mentoring_repo.get_by_mentor_and_mentee(db, user.id, mentee_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="해당 멘티와의 멘토링을 찾을 수 없습니다.")
        return mentoring_repo.get_mentee_statistics(db, mentee_id, mentoring.mentoring_id)

    def create_mentee_feedback(self, db: Session, user: User, mentee_id: uuid.UUID, request: FeedbackCreateRequest):
        mentoring = mentoring_repo.get_by_mentor_and_mentee(db, user.id, mentee_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="해당 멘티와의 멘토링을 찾을 수 없습니다.")
        return feedback_repo.create(db, {
            "mentoring_id": mentoring.mentoring_id,
            "content": request.content,
        })

    def get_mentee_feedbacks(self, db: Session, user: User, mentee_id: uuid.UUID):
        mentoring = mentoring_repo.get_by_mentor_and_mentee(db, user.id, mentee_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="해당 멘티와의 멘토링을 찾을 수 없습니다.")
        return feedback_repo.get_by_mentoring(db, mentoring.mentoring_id)

    def create_assignment_direct(self, db: Session, user: User, request: AssignmentCreateRequest):
        mentoring = mentoring_repo.get_by_mentor_and_mentee(db, user.id, request.mentee_id)
        if not mentoring:
            raise HTTPException(status_code=404, detail="해당 멘티와의 활성화된 멘토링 관계를 찾을 수 없습니다.")
        
        return assignment_repo.create(db, {
            "mentoring_id": mentoring.mentoring_id,
            "title": request.title,
            "description": request.description,
            "due_date": request.due_date,
        })

    def get_all_assignments(self, db: Session, user: User):
        return assignment_repo.get_by_mentor(db, user.id)

    def get_assignment_detail(self, db: Session, user: User, assignment_id: uuid.UUID):
        assignment = assignment_repo.get_by_id_with_submissions(db, assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="과제를 찾을 수 없습니다.")
        mentoring = self._get_mentoring_or_404(db, assignment.mentoring_id)
        if user.id != mentoring.mentor_id:
            raise HTTPException(status_code=403, detail="해당 과제에 대한 권한이 없습니다.")
        return assignment

    def update_assignment_direct(self, db: Session, user: User, assignment_id: uuid.UUID, request: AssignmentUpdateRequest):
        assignment = self.get_assignment_detail(db, user, assignment_id)
        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 데이터가 없습니다.")
        return assignment_repo.update(db, assignment, update_data)

    def grade_assignment(self, db: Session, user: User, assignment_id: uuid.UUID, request: AssignmentGradeRequest):
        assignment = self.get_assignment_detail(db, user, assignment_id)
        update_data = {
            "grade": request.grade,
            "status": AssignmentStatus.GRADED
        }
        return assignment_repo.update(db, assignment, update_data)

    def delete_assignment_direct(self, db: Session, user: User, assignment_id: uuid.UUID):
        assignment = self.get_assignment_detail(db, user, assignment_id)
        assignment_repo.delete(db, assignment)

    def get_all_questions(self, db: Session, user: User):
        return question_repo.get_by_mentor(db, user.id)

    def answer_question_direct(self, db: Session, user: User, question_id: uuid.UUID, request: QuestionAnswerRequest):
        question = question_repo.get_by_id(db, question_id)
        if not question:
            raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
        
        mentoring = self._get_mentoring_or_404(db, question.mentoring_id)
        if user.id != mentoring.mentor_id:
            raise HTTPException(status_code=403, detail="해당 질문에 답변할 권한이 없습니다.")
        
        return question_repo.update(db, question, {
            "answer": request.answer,
            "is_answered": True,
            "answered_at": datetime.utcnow(),
        })


mentoring_service = MentoringService()
