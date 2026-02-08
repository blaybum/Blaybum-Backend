from typing import Optional

import redis.asyncio as aioredis

from app.settings import settings

_async_redis: Optional[aioredis.Redis] = None


async def get_async_redis() -> aioredis.Redis:
    global _async_redis
    if _async_redis is None:
        _async_redis = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password or None,
            db=0,
            decode_responses=True,
        )
    return _async_redis


async def close_async_redis() -> None:
    global _async_redis
    if _async_redis is not None:
        await _async_redis.close()
        _async_redis = None
