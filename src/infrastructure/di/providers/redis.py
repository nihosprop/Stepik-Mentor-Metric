import logging

from collections.abc import AsyncIterable
from typing import NewType

from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from core.main_config import Config

logger = logging.getLogger(__name__)

RedisCache = NewType('RedisCache', Redis)


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
        """
        Provides a RedisCache instance.

        This provider connects to a Redis instance and
            yields a RedisCache instance.
        After the yield statement is done, it closes the connection
            to the Redis instance.
        Delete key 'initial_aggregation_done' of redis instance.

        Args:
            config (Config): The Config instance.

        Yields:
            RedisCache: A RedisCache instance.

        """
        redis = Redis(
            host=config.redis.host,
            port=config.redis.port,
            password=config.redis.password,
            decode_responses=config.redis.decode_responses,
            db=1,
        )
        await redis.delete('initial_aggregation_done')
        yield RedisCache(redis)
        await redis.close()