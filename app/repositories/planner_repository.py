from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.models.models import Planner
from app.repositories.base_repository import BaseRepository
from datetime import date

class PlannerRepository(BaseRepository[Planner]):
    def __init__(self):
        super().__init__(Planner)

    def get_by_user_and_date(self, db: Session, user_id: any, plan_date: date) -> Optional[Planner]:
        return db.query(Planner).filter(
            Planner.user_id == user_id,
            Planner.plan_date == plan_date
        ).first()

    def get_paginated_by_user(
        self,
        db: Session,
        user_id: any,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Planner], int]:
        query = db.query(Planner).filter(Planner.user_id == user_id)

        if start_date:
            query = query.filter(Planner.plan_date >= start_date)
        if end_date:
            query = query.filter(Planner.plan_date <= end_date)

        total_items = query.count()
        planners = query.order_by(Planner.plan_date.desc()).offset(skip).limit(limit).all()

        return planners, total_items

planner_repo = PlannerRepository()
