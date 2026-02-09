from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List

class DailyStudyRecordResponse(BaseModel):
    record_date: date
    day_number: int
    is_fulltime_study: bool
    is_todolist_complete: bool

    model_config = ConfigDict(from_attributes=True)

class MonthlyGrowResponse(BaseModel):
    year: int
    month: int
    records: List[DailyStudyRecordResponse]

class TodayGrowResponse(BaseModel):
    record_date: date
    day_number: int
    is_fulltime_study: bool
    is_todolist_complete: bool

    model_config = ConfigDict(from_attributes=True)
