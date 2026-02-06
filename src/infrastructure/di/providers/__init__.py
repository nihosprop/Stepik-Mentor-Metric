from dishka import Provider

from infrastructure.di.providers.config import ConfigProvider
from infrastructure.di.providers.session import SessionProvider
from infrastructure.di.providers.repositories import RepositoryProvider

PROVIDERS: list[Provider] = [
    ConfigProvider(),
    SessionProvider(),
    RepositoryProvider(),
]

__all__ = [
    'PROVIDERS',
    'ConfigProvider',
    'SessionProvider',
    'RepositoryProvider'
]
