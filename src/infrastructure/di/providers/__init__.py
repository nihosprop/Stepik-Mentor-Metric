from dishka import Provider

from infrastructure.di.providers.config import ConfigProvider
from infrastructure.di.providers.db import PostgresProvider
from infrastructure.di.providers.redis import RedisProvider
from infrastructure.di.providers.repositories import RepositoryProvider

PROVIDERS: list[Provider] = [
    ConfigProvider(),
    PostgresProvider(),
    RepositoryProvider(),
    RedisProvider(),
]

__all__ = [
    'PROVIDERS',
    'ConfigProvider',
    'PostgresProvider',
    'RepositoryProvider',
    'RedisProvider',
]
