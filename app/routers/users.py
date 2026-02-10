import uuid
from typing import Optional
import math
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common_schemas import ResponseModel, PaginatedResponseModel
from app.schemas.user_schemas import UserSearchResponse, SortOrder
from app.models import User
from app.services.user_service import user_service
from app.auth.users import current_active_user

router = APIRouter()


@router.get("/search", response_model=PaginatedResponseModel[UserSearchResponse])
async def search_users(
    search_query: Optional[str] = None,
    role_filter: Optional[str] = None,
    sort_by: SortOrder = SortOrder.name_asc,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    from app.schemas.user_schemas import UserSearchRequest
    
    request = UserSearchRequest(
        search_query=search_query,
        role_filter=role_filter,
        sort_by=sort_by,
        page=page,
        limit=limit
    )
    
    users, total_items = user_service.search_users(db, request)
    
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    
    return {
        "success": True,
        "data": users,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items_per_page": limit
        }
    }


@router.get("/mentors/search", response_model=PaginatedResponseModel[UserSearchResponse])
async def search_mentors(
    search_query: Optional[str] = None,
    sort_by: SortOrder = SortOrder.name_asc,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    mentors, total_items = user_service.search_mentors(
        db=db,
        search_query=search_query,
        sort_by=sort_by,
        page=page,
        limit=limit
    )
    
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    
    return {
        "success": True,
        "data": mentors,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items_per_page": limit
        }
    }


@router.get("/{user_id}", response_model=ResponseModel[UserSearchResponse])
async def get_user_by_id(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    from app.repositories.user_repository import user_repo
    
    target_user = user_repo.get_by_id(db, user_id)
    if not target_user or not target_user.is_active:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    user_response = UserSearchResponse(
        id=target_user.id,
        username=target_user.username,
        full_name=target_user.full_name,
        profile_image=target_user.profile_image,
        role=target_user.role.value,
        created_at=target_user.created_at
    )
    
    return {"success": True, "data": user_response}