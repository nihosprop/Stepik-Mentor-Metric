from dishka import Provider

from .config import ConfigProvider
from .database import DBProvider
from .repositories import RepositoryProvider

PROVIDERS: list[Provider] = [
    ConfigProvider(),
    DBProvider(),
    RepositoryProvider(),
]

__all__: list[str] = [
    'PROVIDERS',
    'ConfigProvider',
    'DBProvider',
    'RepositoryProvider'
]
