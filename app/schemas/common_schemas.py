from typing import Generic, Optional, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

#Global Response
class ResponseModel(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
   
# Pagination
class PaginationInfo(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
class PaginatedResponseModel(BaseModel, Generic[T]):
    success: bool
    data: List[T]
    pagination: PaginationInfo