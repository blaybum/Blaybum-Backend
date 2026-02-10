ㄹfrom fastapi import Depends, HTTPException, status

from app.models.models import User, UserRole
from app.auth.users import current_active_user


async def get_current_mentor(
    user: User = Depends(current_active_user),
) -> User:

    if user.role == UserRole.admin:
        return user
    if user.role != UserRole.mentor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="멘토 권한이 필요합니다.",
        )
    return user


async def get_current_mentee(
    user: User = Depends(current_active_user),
) -> User:

    if user.role == UserRole.admin:
        return user
    if user.role != UserRole.mentee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="멘티 권한이 필요합니다.",
        )
    return user


def require_role(*allowed_roles: UserRole):

    async def role_checker(
        user: User = Depends(current_active_user),
    ) -> User:
        if user.role == UserRole.admin:
            return user
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"허용된 역할: {', '.join([r.value for r in allowed_roles])}",
            )
        return user
    return role_checker
