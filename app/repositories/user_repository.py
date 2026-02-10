from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, asc, desc
from app.repositories.base_repository import BaseRepository
from app.models import User
from app.schemas.user_schemas import SortOrder


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def search_users(
        self, 
        db: Session, 
        search_query: Optional[str] = None,
        role_filter: Optional[str] = None,
        sort_by: SortOrder = SortOrder.name_asc,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[User], int]:
        """
        사용자를 검색하고 페이지네이션과 정렬을 적용합니다.
        
        Returns:
            Tuple[List[User], int]: (사용자 목록, 총 개수)
        """
        query = db.query(User)
        
        # 검색 필터 적용
        filters = []
        
        if search_query:
            search_filter = or_(
                User.username.ilike(f"%{search_query}%"),
                User.full_name.ilike(f"%{search_query}%")
            )
            filters.append(search_filter)
        
        if role_filter:
            filters.append(User.role == role_filter)
        
        # 활성 사용자만 검색 (is_active=True)
        filters.append(User.is_active == True)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # 정렬 적용
        if sort_by == SortOrder.name_asc:
            query = query.order_by(asc(User.full_name), asc(User.username))
        elif sort_by == SortOrder.name_desc:
            query = query.order_by(desc(User.full_name), desc(User.username))
        elif sort_by == SortOrder.uuid_asc:
            query = query.order_by(asc(User.id))
        elif sort_by == SortOrder.uuid_desc:
            query = query.order_by(desc(User.id))
        elif sort_by == SortOrder.newest:
            query = query.order_by(desc(User.created_at))
        elif sort_by == SortOrder.oldest:
            query = query.order_by(asc(User.created_at))
        
        # 총 개수 계산
        total_count = query.count()
        
        # 페이지네이션 적용
        offset = (page - 1) * limit
        users = query.offset(offset).limit(limit).all()
        
        return users, total_count

    def search_mentors(
        self,
        db: Session,
        search_query: Optional[str] = None,
        sort_by: SortOrder = SortOrder.name_asc,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[User], int]:
        """멘토만 검색하는 편의 메서드"""
        return self.search_users(
            db=db,
            search_query=search_query,
            role_filter="mentor",
            sort_by=sort_by,
            page=page,
            limit=limit
        )


user_repo = UserRepository()