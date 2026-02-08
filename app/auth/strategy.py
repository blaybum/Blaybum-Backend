import uuid
from typing import Generic, Optional

import jwt
import redis.asyncio as aioredis

from fastapi_users import exceptions, models
from fastapi_users.authentication.strategy.base import Strategy
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt
from fastapi_users.manager import BaseUserManager

from app.settings import settings

REDIS_ACCESS_PREFIX = "auth:access"
REDIS_REFRESH_PREFIX = "auth:refresh"

ACCESS_AUDIENCE = ["fastapi-users:auth"]
REFRESH_AUDIENCE = ["fastapi-users:refresh"]


class RedisJWTStrategy(Strategy[models.UP, models.ID], Generic[models.UP, models.ID]):

    def __init__(
        self,
        redis: aioredis.Redis,
        secret: SecretType,
        lifetime_seconds: int,
        algorithm: str = "HS256",
    ):
        self.redis = redis
        self.secret = secret
        self.lifetime_seconds = lifetime_seconds
        self.algorithm = algorithm

    async def write_token(self, user: models.UP) -> str:
        jti = str(uuid.uuid4())
        data = {
            "sub": str(user.id),
            "aud": ACCESS_AUDIENCE,
            "jti": jti,
        }
        token = generate_jwt(
            data, self.secret, self.lifetime_seconds, algorithm=self.algorithm
        )

        redis_key = f"{REDIS_ACCESS_PREFIX}:{jti}"
        await self.redis.setex(redis_key, self.lifetime_seconds, str(user.id))

        return token

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Optional[models.UP]:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token, self.secret, ACCESS_AUDIENCE, algorithms=[self.algorithm]
            )
            user_id = data.get("sub")
            jti = data.get("jti")
            if user_id is None or jti is None:
                return None
        except jwt.PyJWTError:
            return None

        redis_key = f"{REDIS_ACCESS_PREFIX}:{jti}"
        try:
            stored = await self.redis.get(redis_key)
        except (aioredis.ConnectionError, aioredis.TimeoutError):
            return None

        if stored is None:
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def destroy_token(self, token: str, user: models.UP) -> None:
        try:
            data = decode_jwt(
                token, self.secret, ACCESS_AUDIENCE, algorithms=[self.algorithm]
            )
            jti = data.get("jti")
            if jti:
                await self.redis.delete(f"{REDIS_ACCESS_PREFIX}:{jti}")
        except jwt.PyJWTError:
            pass


class RefreshTokenManager:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self.secret = settings.secret_key
        self.algorithm = settings.algorithm
        self.lifetime_seconds = settings.refresh_token_expire_days * 24 * 60 * 60

    async def create_refresh_token(self, user_id: str) -> str:
        jti = str(uuid.uuid4())
        data = {
            "sub": user_id,
            "aud": REFRESH_AUDIENCE,
            "jti": jti,
        }
        token = generate_jwt(
            data, self.secret, self.lifetime_seconds, algorithm=self.algorithm
        )

        redis_key = f"{REDIS_REFRESH_PREFIX}:{jti}"
        await self.redis.setex(redis_key, self.lifetime_seconds, user_id)

        return token

    async def validate_refresh_token(self, token: str) -> Optional[str]:
        try:
            data = decode_jwt(
                token, self.secret, REFRESH_AUDIENCE, algorithms=[self.algorithm]
            )
            user_id = data.get("sub")
            jti = data.get("jti")
            if user_id is None or jti is None:
                return None
        except jwt.PyJWTError:
            return None

        redis_key = f"{REDIS_REFRESH_PREFIX}:{jti}"
        try:
            stored = await self.redis.get(redis_key)
        except (aioredis.ConnectionError, aioredis.TimeoutError):
            return None

        if stored is None:
            return None

        return user_id

    async def revoke_refresh_token(self, token: str) -> None:
        try:
            data = decode_jwt(
                token, self.secret, REFRESH_AUDIENCE, algorithms=[self.algorithm]
            )
            jti = data.get("jti")
            if jti:
                await self.redis.delete(f"{REDIS_REFRESH_PREFIX}:{jti}")
        except jwt.PyJWTError:
            pass
