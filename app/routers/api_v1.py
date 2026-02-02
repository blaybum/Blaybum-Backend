from fastapi import APIRouter
from app.routers import planners

api_v1_router = APIRouter()

api_v1_router.include_router(planners.router, prefix="/planners", tags=["Planners"])