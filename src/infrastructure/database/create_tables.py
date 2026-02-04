import logging

from sqlalchemy.ext.asyncio import AsyncEngine

from db.models.base import Base

logger = logging.getLogger(__name__)


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.connect() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()
