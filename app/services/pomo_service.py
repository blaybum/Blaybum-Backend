import uuid
from typing import List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.models import User, Pomo, Concentration
from app.repositories.pomo_repository import pomo_repo
from app.repositories.concentration_repository import concentration_repo
from app.schemas.pomo_schemas import PomoCreateRequest, PomoUpdateRequest, ConcentrationCreate

class PomoService:
    def create_pomo(self, db: Session, user: User, request: PomoCreateRequest) -> Pomo:
        pomo_data = {
            "user_id": user.id,
            "planner_id": request.planner_id,
            "todo_id": request.todo_id,
            "real_start_time": request.real_start_time or None,
            "real_end_time": request.real_end_time or None,
            "edit_start_time": request.real_start_time or None,
            "edit_end_time": request.real_end_time or None,
        }
        return pomo_repo.create(db, pomo_data)

    def get_pomo(self, db: Session, user: User, pomo_id: uuid.UUID) -> Pomo:
        pomo = pomo_repo.get_by_id(db, pomo_id)
        if not pomo or pomo.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="포모도로 기록을 찾을 수 없거나 접근 권한이 없습니다."
            )
        return pomo

    def get_pomos(
        self, db: Session, user: User, page: int = 1, limit: int = 10
    ) -> Tuple[List[Pomo], int]:
        skip = (page - 1) * limit
        return pomo_repo.get_paginated_by_user(db, user.id, skip, limit)

    def update_pomo(self, db: Session, user: User, pomo_id: uuid.UUID, request: PomoUpdateRequest) -> Pomo:
        pomo = self.get_pomo(db, user, pomo_id)
        update_data = request.model_dump(exclude_unset=True)
        return pomo_repo.update(db, pomo, update_data)

    def delete_pomo(self, db: Session, user: User, pomo_id: uuid.UUID) -> None:
        pomo = self.get_pomo(db, user, pomo_id)
        pomo_repo.delete(db, pomo)

    def add_concentration_log(
        self, db: Session, user: User, pomo_id: uuid.UUID, request: ConcentrationCreate
    ) -> Concentration:
        pomo = self.get_pomo(db, user, pomo_id)
        log_data = {
            "pomo_id": pomo.id,
            "event_type": request.event_type,
            "timestamp": request.timestamp or None
        }
        return concentration_repo.create(db, log_data)

pomo_service = PomoService()
