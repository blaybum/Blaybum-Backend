from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date
from app.repositories.base_repository import BaseRepository
from app.models.models import DailyStudyRecord

class GrowRepository(BaseRepository[DailyStudyRecord]):
    def __init__(self):
        super().__init__(DailyStudyRecord)

    def get_by_user_and_date(self, db: Session, user_id: any, record_date: date) -> Optional[DailyStudyRecord]:
        return db.query(DailyStudyRecord).filter(
            DailyStudyRecord.user_id == user_id,
            DailyStudyRecord.record_date == record_date
        ).first()

    def get_monthly_records(self, db: Session, user_id: any, year: int, month: int) -> List[DailyStudyRecord]:
        return db.query(DailyStudyRecord).filter(
            DailyStudyRecord.user_id == user_id,
            DailyStudyRecord.record_date.cast(str).like(f"{year}-{month:02d}-%")
        ).order_by(DailyStudyRecord.record_date.asc()).all()

grow_repo = GrowRepository()
