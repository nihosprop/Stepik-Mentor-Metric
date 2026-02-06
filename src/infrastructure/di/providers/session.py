import logging

from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.main_config import Config

logger = logging.getLogger(__name__)

class SessionProvider(Provider):
    @provide(scope=Scope.APP)
    def get_engine(self, config: Config) -> AsyncEngine:
        engine = create_async_engine(config.postgres.get_dsn())
        return engine

    @provide(scope=Scope.APP)
    def get_sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession]:
        async with sessionmaker() as session:
            logger.debug('Session opened')
            try:
                yield session
                await session.commit()
                logger.debug('Session committed')
            except Exception:
                await session.rollback()
                logger.debug('Session rollback')
                raise
            finally:
                await session.close()
                logger.debug('Session closed')
