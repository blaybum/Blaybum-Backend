import sys
import uuid
import enum
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyBaseOAuthAccountTableUUID
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, String, Text,
    Date, Time, Integer, Enum, UniqueConstraint, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base

class DayOfWeek(str, enum.Enum):
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"
    SUN = "SUN"

class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TodoStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class UserRole(str, enum.Enum):
    mentor = "mentor"
    mentee = "mentee"
    admin = "admin"

class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    __tablename__ = "oauth_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

class PomoCategory(str, enum.Enum):
    MATH = "수학"
    ENGLISH = "영어"
    KOREAN = "국어"
    SCIENCE = "과학"
    SOCIETY = "사회"
    ETC = "기타"

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    username = Column(String(100), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=True)
    profile_image = Column(String(500), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.mentee, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    oauth_accounts: Mapped[List[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined", cascade="all, delete-orphan"
    )

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    planners = relationship("Planner", back_populates="user", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author = relationship("User", back_populates="posts")


class Planner(Base):
    __tablename__ = "planners"

    planner_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_date = Column(Date, nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=True)
    daily_goal = Column(Integer, default=0)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="planners")
    todos = relationship("Todo", back_populates="planner", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('user_id', 'plan_date', name='unique_user_plan_date'),
        Index('idx_planners_user_date', 'user_id', 'plan_date'),
    )


class Todo(Base):
    __tablename__ = "todos"

    todo_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planner_id = Column(UUID(as_uuid=True), ForeignKey("planners.planner_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_time = Column(Time, nullable=True)
    priority = Column(Enum(Priority), nullable=True)
    status = Column(Enum(TodoStatus), default=TodoStatus.pending)
    estimated_duration_minutes = Column(Integer, nullable=True)
    actual_duration_minutes = Column(Integer, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    planner = relationship("Planner", back_populates="todos")

    __table_args__ = (
        Index('idx_todos_planner', 'planner_id'),
        Index('idx_todos_status', 'status'),
    )

class Pomo(Base):
    __tablename__ = "pomo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    planner_id = Column(UUID(as_uuid=True), ForeignKey("planners.planner_id", ondelete="SET NULL"), nullable=True)
    todo_id = Column(UUID(as_uuid=True), ForeignKey("todos.todo_id", ondelete="SET NULL"), nullable=True)
    category = Column(Enum(PomoCategory), nullable=False, server_default=PomoCategory.ETC.value)
    real_start_time = Column(DateTime(timezone=True), server_default=func.now())
    real_end_time = Column(DateTime(timezone=True), server_default=func.now())
    edit_start_time = Column(DateTime(timezone=True), server_default=func.now())
    edit_end_time = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def distraction_count(self) -> int:
        if not hasattr(self, "concentration_logs"):
            return 0
        return len([log for log in self.concentration_logs if log.event_type == "PICK_UP"])

    __table_args__ = (
        Index('idx_pomo_user', 'user_id'),
        Index('idx_pomo_todo', 'todo_id'),
    )

class UsageEventType(str, enum.Enum):
    PICK_UP = "PICK_UP"
    PUT_DOWN = "PUT_DOWN"

class Concentration(Base):
    __tablename__ = "concentration"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pomo_id = Column(UUID(as_uuid=True), ForeignKey("pomo.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(Enum(UsageEventType), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    pomo = relationship("Pomo", backref="concentration_logs")