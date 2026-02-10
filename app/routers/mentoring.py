import uuid
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

router = APIRouter()

@router.post("/", response_model=ResponseModel[], status_code=status.HTTP_201_CREATED)
async def create_mentoring_session(