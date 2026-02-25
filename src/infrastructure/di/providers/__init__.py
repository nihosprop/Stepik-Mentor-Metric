from dishka import Provider

from infrastructure.di.providers.bot import BotProvider
from infrastructure.di.providers.config import ConfigProvider
from infrastructure.di.providers.db import PostgresProvider
from infrastructure.di.providers.http import HttpProvider
from infrastructure.di.providers.redis import RedisProvider
from infrastructure.di.providers.repositories import RepositoryProvider
from infrastructure.di.providers.stepik_client import StepikProvider

PROVIDERS: list[Provider] = [
    ConfigProvider(),
    PostgresProvider(),
    RepositoryProvider(),
    RedisProvider(),
    HttpProvider(),
    StepikProvider(),
    BotProvider(),
]

__all__ = [
    'PROVIDERS',
    'ConfigProvider',
    'PostgresProvider',
    'RepositoryProvider',
    'RedisProvider',
    'HttpProvider',
    'StepikProvider',
    'BotProvider',
]
