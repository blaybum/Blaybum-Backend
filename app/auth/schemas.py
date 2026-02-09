import uuid
from enum import Enum
from typing import Optional

from fastapi_users import schemas
from pydantic import Field


class UserRole(str, Enum):
    mentor = "mentor"
    mentee = "mentee"


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    role: UserRole = UserRole.mentee


class UserCreate(schemas.BaseUserCreate):
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole = UserRole.mentee


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    role: Optional[UserRole] = None
