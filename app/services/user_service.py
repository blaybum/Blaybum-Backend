from typing import List, Tuple
from sqlalchemy.orm import Session
from app.repositories.user_repository import user_repo
from app.schemas.user_schemas import UserSearchRequest, UserSearchResponse, SortOrder


class UserService:
    
    def search_users(
        self, 
        db: Session, 
        request: UserSearchRequest
    ) -> Tuple[List[UserSearchResponse], int]:
        """
        사용자를 검색하고 UserSearchResponse로 변환합니다.
        
        Returns:
            Tuple[List[UserSearchResponse], int]: (사용자 목록, 총 개수)
        """
        users, total_count = user_repo.search_users(
            db=db,
            search_query=request.search_query,
            role_filter=request.role_filter,
            sort_by=request.sort_by,
            page=request.page,
            limit=request.limit
        )
        
        user_responses = [
            UserSearchResponse(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                profile_image=user.profile_image,
                role=user.role.value,  # Enum을 문자열로 변환
                created_at=user.created_at
            )
            for user in users
        ]
        
        return user_responses, total_count
    
    def search_mentors(
        self,
        db: Session,
        search_query: str = None,
        sort_by: SortOrder = SortOrder.name_asc,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[UserSearchResponse], int]:
        """멘토만 검색하는 편의 메서드"""
        request = UserSearchRequest(
            search_query=search_query,
            role_filter="mentor",
            sort_by=sort_by,
            page=page,
            limit=limit
        )
        return self.search_users(db, request)


user_service = UserService()