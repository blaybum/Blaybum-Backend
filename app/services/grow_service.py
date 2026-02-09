import uuid
from datetime import date, datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import User, Pomo, Todo, Planner, DailyStudyRecord
from app.repositories import grow_repo, pomo_repo, todo_repo, planner_repo

class GrowService:
    def calculate_daily_achievement(self, db: Session, user_id: uuid.UUID, target_date: date) -> DailyStudyRecord:
        study_time_seconds = db.query(
            func.sum(func.extract('epoch', Pomo.real_end_time - Pomo.real_start_time))
        ).filter(
            Pomo.user_id == user_id,
            func.cast(Pomo.real_start_time, func.Date) == target_date
        ).scalar() or 0
        study_time_minutes = int(study_time_seconds / 60)

        planner = planner_repo.get_by_user_and_date(db, user_id, target_date)
        daily_goal = planner.daily_goal if planner else 0
        is_fulltime_study = study_time_minutes >= daily_goal if daily_goal > 0 else False

        if planner:
            todos = todo_repo.get_all_by_planner(db, planner.planner_id)
            is_todolist_complete = all(t.status == "completed" for t in todos) if todos else False
        else:
            is_todolist_complete = False

        day_number = target_date.day 

        existing_record = grow_repo.get_by_user_and_date(db, user_id, target_date)
        record_data = {
            "user_id": user_id,
            "record_date": target_date,
            "day_number": day_number,
            "is_fulltime_study": is_fulltime_study,
            "is_todolist_complete": is_todolist_complete
        }

        if existing_record:
            return grow_repo.update(db, existing_record, record_data)
        else:
            return grow_repo.create(db, record_data)

    def get_monthly_field(self, db: Session, user: User, year: int, month: int) -> List[DailyStudyRecord]:
        return grow_repo.get_monthly_records(db, user.id, year, month)

grow_service = GrowService()
