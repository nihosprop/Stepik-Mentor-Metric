from dishka import Provider

from infrastructure.di.providers.config import ConfigProvider
from infrastructure.di.providers.db import SessionProvider
from infrastructure.di.providers.redis import RedisProvider
from infrastructure.di.providers.repositories import RepositoryProvider

PROVIDERS: list[Provider] = [
    ConfigProvider(),
    SessionProvider(),
    RepositoryProvider(),
    RedisProvider(),
]

__all__ = [
    'PROVIDERS',
    'ConfigProvider',
    'SessionProvider',
    'RepositoryProvider',
    'RedisProvider',
]
