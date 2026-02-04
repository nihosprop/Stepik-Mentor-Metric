from dishka import Provider

from infrastructure.di.providers.config import ConfigProvider
from infrastructure.di.providers.database import DBProvider
from infrastructure.di.providers.repositories import RepositoryProvider

PROVIDERS: list[Provider] = [
    ConfigProvider(),
    DBProvider(),
    RepositoryProvider(),
]

__all__ = [
    'PROVIDERS',
    'ConfigProvider',
    'DBProvider',
    'RepositoryProvider'
]
