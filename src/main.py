import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from bot.dialogs.start.dialog import start_dialog
from bot.dialogs.start.handlers import start_router
from bot.providers import ConfigProvider, DBProvider
from core.logger import setup_logging
from core.main_config import main_config

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    logger.info('Logging setup complete')

    bot = Bot(token=main_config.bot.token)
    logger.info('Bot instance created')

    dp = Dispatcher()
    logger.info('DP instance created')

    #Dishka
    container = make_async_container(ConfigProvider(), DBProvider())
    setup_dishka(container=container, router=dp)
    logger.info('Dishka setup complete')

    # Routers
    dp.include_routers(start_router, start_dialog)
    logger.info('Include routers complete')

    #Dialogs
    setup_dialogs(dp)
    logger.info('Dialogs setup complete')

    try:
        logger.info('Starting loop')
        await dp.start_polling(bot)
    finally:
        await container.close()
        logger.info('Shutting down')


if __name__ == '__main__':
    asyncio.run(main())
