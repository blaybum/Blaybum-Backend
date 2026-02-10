import uuid
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class SortOrder(str, Enum):
  name_asc = "name_asc"
  name_desc = "name_desc"
  uuid_asc = "uuid_asc"
  uuid_desc = "uuid_desc"
  newest = "newest"
  oldest = "oldest"

class UserSearchResponse(BaseModel):
  id: uuid.UUID
  username: Optional[str] = None
  full_name: Optional[str] = None
  profile_image: Optional[str] = None
  role: str
  created_at: datetime

  model_config = ConfigDict(from_attributes=True)

class UserSearchRequest(BaseModel):
  search_query: Optional[str] = Field(None, description="검색할 멘토 이름")
  role_filter: Optional[str] = Field(None, description="역할 필터 (mentor/mentee)")
  sort_by: SortOrder = Field(SortOrder.name_asc, description="정렬 방식")
  page: int = Field(1, ge=1, description="페이지 번호")
  limit: int = Field(10, ge=1, le=100, description="페이지당 항목 수")