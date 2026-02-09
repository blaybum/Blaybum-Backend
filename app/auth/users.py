import uuid

from fastapi import Depends
from fastapi_users import FastAPIUsers

from app.models.models import User
from app.auth.backend import auth_backend
from app.auth.manager import get_user_manager


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
current_verified_user = fastapi_users.current_user(active=True, verified=True)
optional_current_user = fastapi_users.current_user(active=True, optional=True)
