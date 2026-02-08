import redis.asyncio as aioredis
from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend, BearerTransport

from app.auth.redis import get_async_redis
from app.auth.strategy import RedisJWTStrategy
from app.settings import settings

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


async def get_jwt_strategy(
    redis: aioredis.Redis = Depends(get_async_redis),
) -> RedisJWTStrategy:
    return RedisJWTStrategy(
        redis=redis,
        secret=settings.secret_key,
        lifetime_seconds=settings.access_token_expire_minutes * 60,
        algorithm=settings.algorithm,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
