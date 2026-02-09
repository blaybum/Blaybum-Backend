from typing import Optional

import jwt as pyjwt
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import BaseOAuth2, OAuth2Token

from fastapi_users.authentication import Strategy
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.jwt import decode_jwt, generate_jwt
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode

from app.auth.backend import auth_backend
from app.auth.manager import get_user_manager
from app.auth.oauth import google_oauth_client, kakao_oauth_client
from app.auth.redis import get_async_redis
from app.auth.schemas import UserRead, UserCreate, UserUpdate
from app.auth.strategy import RefreshTokenManager
from app.auth.token_schemas import LogoutRequest, RefreshTokenRequest, TokenPairResponse
from app.auth.users import fastapi_users
from app.models.models import User
from app.settings import settings

auth_router = APIRouter()

STATE_TOKEN_AUDIENCE = "fastapi-users:oauth-state"


jwt_router = APIRouter(prefix="/jwt", tags=["Auth - JWT"])


@jwt_router.post("/login", response_model=TokenPairResponse)
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager = Depends(get_user_manager),
    strategy: Strategy = Depends(auth_backend.get_strategy),
    redis: aioredis.Redis = Depends(get_async_redis),
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    access_token = await strategy.write_token(user)

    refresh_mgr = RefreshTokenManager(redis)
    refresh_token = await refresh_mgr.create_refresh_token(str(user.id))

    await user_manager.on_after_login(user, request)

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@jwt_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    body: LogoutRequest = LogoutRequest(),
    user_token: tuple = Depends(
        fastapi_users.authenticator.current_user_token(active=True)
    ),
    strategy: Strategy = Depends(auth_backend.get_strategy),
    redis: aioredis.Redis = Depends(get_async_redis),
):
    user, token = user_token
    await strategy.destroy_token(token, user)

    if body.refresh_token:
        refresh_mgr = RefreshTokenManager(redis)
        await refresh_mgr.revoke_refresh_token(body.refresh_token)


@jwt_router.post("/refresh", response_model=TokenPairResponse)
async def refresh(
    body: RefreshTokenRequest,
    user_manager: BaseUserManager = Depends(get_user_manager),
    strategy: Strategy = Depends(auth_backend.get_strategy),
    redis: aioredis.Redis = Depends(get_async_redis),
):
    refresh_mgr = RefreshTokenManager(redis)

    user_id = await refresh_mgr.validate_refresh_token(body.refresh_token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_REFRESH_TOKEN",
        )

    try:
        parsed_id = user_manager.parse_id(user_id)
        user = await user_manager.get(parsed_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_REFRESH_TOKEN",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="USER_INACTIVE",
        )

    await refresh_mgr.revoke_refresh_token(body.refresh_token)

    new_access_token = await strategy.write_token(user)
    new_refresh_token = await refresh_mgr.create_refresh_token(str(user.id))

    return TokenPairResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


auth_router.include_router(jwt_router)


auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=["Auth - Register"],
)

auth_router.include_router(
    fastapi_users.get_reset_password_router(),
    tags=["Auth - Password"],
)

auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
    tags=["Auth - Verify"],
)

auth_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["Auth - Users"],
)


def _generate_state_token(data: dict, secret: str, lifetime_seconds: int = 3600) -> str:
    data["aud"] = STATE_TOKEN_AUDIENCE
    return generate_jwt(data, secret, lifetime_seconds)


def create_oauth_router_with_refresh(
    oauth_client: BaseOAuth2,
    redirect_url: str,
    associate_by_email: bool = True,
) -> APIRouter:
    """OAuth authorize + callback 라우터를 생성한다. callback에서 TokenPairResponse를 반환."""
    router = APIRouter()

    oauth2_authorize_callback = OAuth2AuthorizeCallback(
        oauth_client,
        redirect_url=redirect_url,
    )

    @router.get("/authorize")
    async def authorize(
        request: Request,
        scopes: list[str] = Query(None),
    ):
        state_data: dict = {}
        state = _generate_state_token(state_data, settings.secret_key)
        authorization_url = await oauth_client.get_authorization_url(
            redirect_url, state, scopes
        )
        return {"authorization_url": authorization_url}

    @router.get("/callback", response_model=TokenPairResponse)
    async def callback(
        request: Request,
        access_token_state: tuple[OAuth2Token, str] = Depends(oauth2_authorize_callback),
        user_manager: BaseUserManager = Depends(get_user_manager),
        strategy: Strategy = Depends(auth_backend.get_strategy),
        redis: aioredis.Redis = Depends(get_async_redis),
    ):
        token, state = access_token_state
        account_id, account_email = await oauth_client.get_id_email(
            token["access_token"]
        )

        if account_email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.OAUTH_NOT_AVAILABLE_EMAIL,
            )

        try:
            decode_jwt(state, settings.secret_key, [STATE_TOKEN_AUDIENCE])
        except pyjwt.DecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        try:
            user = await user_manager.oauth_callback(
                oauth_client.name,
                token["access_token"],
                account_id,
                account_email,
                token.get("expires_at"),
                token.get("refresh_token"),
                request,
                associate_by_email=associate_by_email,
                is_verified_by_default=False,
            )
        except UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.OAUTH_USER_ALREADY_EXISTS,
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )

        access_token = await strategy.write_token(user)
        refresh_mgr = RefreshTokenManager(redis)
        refresh_token = await refresh_mgr.create_refresh_token(str(user.id))

        await user_manager.on_after_login(user, request)

        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    return router


if settings.google_client_id and settings.google_client_secret:
    auth_router.include_router(
        create_oauth_router_with_refresh(
            google_oauth_client,
            redirect_url=f"{settings.oauth_redirect_url}/google",
        ),
        prefix="/google",
        tags=["Auth - Google OAuth"],
    )

    auth_router.include_router(
        fastapi_users.get_oauth_associate_router(
            google_oauth_client,
            UserRead,
            settings.secret_key,
            redirect_url=f"{settings.oauth_redirect_url}/google",
        ),
        prefix="/google/associate",
        tags=["Auth - Google OAuth"],
    )

if settings.kakao_client_id and settings.kakao_client_secret:
    auth_router.include_router(
        create_oauth_router_with_refresh(
            kakao_oauth_client,
            redirect_url=f"{settings.oauth_redirect_url}/kakao",
        ),
        prefix="/kakao",
        tags=["Auth - Kakao OAuth"],
    )

    auth_router.include_router(
        fastapi_users.get_oauth_associate_router(
            kakao_oauth_client,
            UserRead,
            settings.secret_key,
            redirect_url=f"{settings.oauth_redirect_url}/kakao",
        ),
        prefix="/kakao/associate",
        tags=["Auth - Kakao OAuth"],
    )
