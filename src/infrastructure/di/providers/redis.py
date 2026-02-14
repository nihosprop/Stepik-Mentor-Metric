from collections.abc import AsyncGenerator
from typing import NewType

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from core.main_config import main_config

CacheRedis = NewType("CacheRedis", Redis)
StorageRedis = NewType("StorageRedis", Redis)

class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def redis_cache(self) -> AsyncGenerator[CacheRedis]:
        redis = Redis(
            host=main_config.redis.host,
            port=main_config.redis.port,
            password=main_config.redis.password,
            db=0)
        yield CacheRedis(redis)
        await redis.close()

    @provide(scope=Scope.APP)
    async def redis_storage(self) -> AsyncGenerator[StorageRedis]:
        redis = Redis(
            host=main_config.redis.host,
            port=main_config.redis.port,
            password=main_config.redis.password,
            db=1
        )
        yield StorageRedis(redis)
        await redis.close()
