from sqlalchemy.orm import Session
from app.repositories.planner_repository import planner_repo
from app.schemas import PlannerCreateRequest, PlannerUpdateRequest
from app.models.models import DayOfWeek, User
from fastapi import HTTPException, status
import uuid
from datetime import date

class PlannerService:
    def create_planner(self, db: Session, user: User, request: PlannerCreateRequest):
        day_name = request.plan_date.strftime("%a").upper()
        try:
            day_of_week = DayOfWeek[day_name]
        except KeyError:
            day_of_week = DayOfWeek.MON

        existing_planner = planner_repo.get_by_user_and_date(db, user.id, request.plan_date)
        if existing_planner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 {request.plan_date}에 대한 플래너가 존재합니다."
            )

        new_planner_data = {
            "user_id": user.id,
            "plan_date": request.plan_date,
            "day_of_week": day_of_week,
            "daily_goal": 0,
            "memo": ""
        }
        return planner_repo.create(db, new_planner_data)

    def get_planner(self, db: Session, user: User, planner_id: uuid.UUID):
        planner = planner_repo.get_by_id(db, planner_id)
        if not planner or planner.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="플래너를 찾을 수 없거나 조회 권한이 없습니다."
            )
        return planner

    def get_planners(self, db: Session, user: User, start_date: date, end_date: date, page: int, limit: int):
        skip = (page - 1) * limit
        return planner_repo.get_paginated_by_user(db, user.id, start_date, end_date, skip, limit)

    def update_planner(self, db: Session, user: User, planner_id: uuid.UUID, request: PlannerUpdateRequest):
        planner = self.get_planner(db, user, planner_id)
        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 데이터가 제공되지 않았습니다.")
        return planner_repo.update(db, planner, update_data)

    def delete_planner(self, db: Session, user: User, planner_id: uuid.UUID):
        planner = self.get_planner(db, user, planner_id)
        planner_repo.delete(db, planner)

planner_service = PlannerService()
