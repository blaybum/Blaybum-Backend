import sys
import uuid
import enum
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, String, Text, 
    Date, Time, Integer, Enum, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
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

    # Relationships
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

    # Relationships
    planner = relationship("Planner", back_populates="todos")

    __table_args__ = (
        Index('idx_todos_planner', 'planner_id'),
        Index('idx_todos_status', 'status'),
    )