from typing import List, Tuple
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.models import Pomo

class PomoRepository(BaseRepository[Pomo]):
    def __init__(self):
        super().__init__(Pomo)

    def get_paginated_by_user(
        self,
        db: Session,
        user_id: any,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Pomo], int]:
        query = db.query(Pomo).filter(Pomo.user_id == user_id)
        total_items = query.count()
        pomos = query.order_by(Pomo.created_at.desc()).offset(skip).limit(limit).all()
        return pomos, total_items

pomo_repo = PomoRepository()