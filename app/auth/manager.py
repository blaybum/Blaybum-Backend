import uuid
from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from app.models.models import User, OAuthAccount
from app.auth.db import get_user_db
from app.settings import settings


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):

    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"사용자 등록 완료: {user.email}")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"비밀번호 재설정 토큰 발급: {user.email}, token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"이메일 인증 토큰 발급: {user.email}, token: {token}")

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[any] = None,
    ):
        print(f"사용자 로그인: {user.email}")

    async def on_after_oauth_callback(
        self,
        user: User,
        oauth_name: str,
        request: Optional[Request] = None,
    ):
        print(f"OAuth 로그인 완료: {user.email} via {oauth_name}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
