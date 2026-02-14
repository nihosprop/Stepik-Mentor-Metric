from collections.abc import AsyncIterable
from typing import NewType

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from core.main_config import Config

CacheRedis = NewType('CacheRedis', Redis)
StorageRedis = NewType('StorageRedis', Redis)


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def redis_cache(self, config: Config) -> AsyncIterable[CacheRedis]:
        redis = Redis(
            host=config.redis.host,
            port=config.redis.port,
            password=config.redis.password,
            decode_responses=config.redis.decode_responses,
            db=0,
        )
        yield CacheRedis(redis)
        await redis.close()

    @provide(scope=Scope.APP)
    async def redis_storage(
        self, config: Config
    ) -> AsyncIterable[StorageRedis]:
        redis = Redis(
            host=config.redis.host,
            port=config.redis.port,
            password=config.redis.password,
            decode_responses=config.redis.decode_responses,
            db=1,
        )
        yield StorageRedis(redis)
        await redis.close()
