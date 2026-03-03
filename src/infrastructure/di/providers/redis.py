import logging

from collections.abc import AsyncIterable

from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from core.main_config import Config

RedisCache = Redis

logger = logging.getLogger(__name__)


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def redis_storage(
        self, config: Config
    ) -> AsyncIterable[RedisStorage]:
        redis = Redis(
            host=config.redis.host,
            port=config.redis.port,
            password=config.redis.password,
            decode_responses=True,
            db=0,
        )
        yield RedisStorage(
            redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True)
        )
        await redis.close()

    @provide(scope=Scope.APP)
    async def redis_cache(self, config: Config) -> AsyncIterable[RedisCache]:
        redis = RedisCache(
            host=config.redis.host,
            port=config.redis.port,
            password=config.redis.password,
            decode_responses=config.redis.decode_responses,
            db=1,
        )
        yield redis
        await redis.close()
