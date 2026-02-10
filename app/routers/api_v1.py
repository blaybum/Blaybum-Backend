from fastapi import APIRouter
from app.routers import planners, todos, statistics, pomo
from app.routers.auth import auth_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(planners.router, prefix="/planners", tags=["Planners"])
api_v1_router.include_router(todos.router, prefix="/todos", tags=["Todos"])
api_v1_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
api_v1_router.include_router(pomo.router, prefix="/pomos", tags=["Pomo"])
api_v1_router.include_router(mentoring.router, prefix="/mentoring", tags=["Mentoring"])