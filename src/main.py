import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import setup_dishka
from sqlalchemy.ext.asyncio import AsyncEngine

from bot.dialogs.start.dialog import start_dialog
from bot.dialogs.start.handlers import start_router
from bot.providers import ConfigProvider, DBProvider
from core.logger import setup_logging
from core.main_config import main_config
from db.create_tables import create_tables

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    logger.info('Logging setup complete')

    bot = Bot(token=main_config.bot.token)
    logger.info('Bot instance created')
    dp = Dispatcher()
    logger.info('Dispatcher instance created')

    container: AsyncContainer = make_async_container(
        ConfigProvider(), DBProvider()
    )

    engine: AsyncEngine = await container.get(AsyncEngine)

    await create_tables(engine)
    logger.info('Database tables synced')

    setup_dishka(container=container, router=dp, auto_inject=True)
    logger.info('Dishka setup complete')

    # Routers
    dp.include_routers(start_router, start_dialog)
    logger.info('Include routers complete')

    # Dialogs
    setup_dialogs(dp)
    logger.info('Dialogs setup complete')

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        logger.info('Starting loop')
        await dp.start_polling(bot)
    finally:
        dp.shutdown.register(container.close)
        # await container.close()
        logger.info('Dishka container closed')
        logger.info('Closing loop')


if __name__ == '__main__':
    asyncio.run(main())
