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


class PostgresProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self, config: Config) -> AsyncEngine:
        engine = create_async_engine(
            config.postgres.get_dsn(),
            pool_size=5,
            max_overflow=3,
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_timeout=10,
            echo=False,
            pool_use_lifo=True,
        )
        logger.info(f'🗄️DB Pool initialized: {engine.pool.status()}')

        return engine

    @provide(scope=Scope.APP)
    def sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

    @provide(scope=Scope.REQUEST)
    async def session(
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
