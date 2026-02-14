import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import setup_dishka

from bot.dialogs import ROUTERS
from core.logger import setup_logging
from core.main_config import main_config
from infrastructure.di.providers import PROVIDERS

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    logger.info('Logging setup complete')

    container: AsyncContainer = make_async_container(*PROVIDERS)
    logger.info('Dishka container created')

    bot = Bot(token=main_config.bot.token)
    logger.info('Bot instance created')
    dp = Dispatcher()
    logger.info('Dispatcher instance created')

    setup_dishka(container=container, router=dp, auto_inject=True)
    logger.info('Dishka setup complete')

    # Routers
    dp.include_routers(*ROUTERS)
    logger.info('Include routers complete')

    # Dialogs
    setup_dialogs(dp)
    logger.info('Dialogs setup complete')

    # Run bot
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        logger.info('Starting polling...')
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(e)
    finally:
        await container.close()
        logger.info('Dishka container closed')
        logger.info('Polling closed')


if __name__ == '__main__':
    asyncio.run(main())
