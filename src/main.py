import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownState
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import setup_dishka

from bot.commands import set_main_menu
from bot.dialogs import DIALOGS, ROUTERS
from bot.dialogs.common.errors import on_unknown_state
from bot.middlewares.acl import ACLMiddleware
from core.logger import setup_logging
from infrastructure.di.providers import PROVIDERS

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    logger.info('Logging setup complete')

    container: AsyncContainer = make_async_container(*PROVIDERS)
    logger.info('Dishka container created')

    bot = await container.get(Bot)
    logger.info('Bot instance created')

    storage = await container.get(RedisStorage)
    dp = Dispatcher(storage=storage)

    await set_main_menu(bot=bot)

    logger.info('Dispatcher instance created')

    setup_dishka(container=container, router=dp, auto_inject=True)
    logger.info('Dishka setup complete')

    # Middlewares
    dp.update.middleware(ACLMiddleware())

    # Error handlers
    dp.errors.register(on_unknown_state, ExceptionTypeFilter(UnknownState))

    # Routers
    dp.include_routers(*ROUTERS)
    logger.info('Include routers complete')

    # Dialogs
    dp.include_routers(*DIALOGS)
    logger.info('Include dialogs complete')

    setup_dialogs(dp)
    logger.info('Dialogs setup complete')

    # Run bot
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        logger.info('Starting polling...')
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(e, exc_info=True)
    finally:
        await container.close()
        logger.info('Dishka container closed')
        logger.info('Polling closed')


if __name__ == '__main__':
    asyncio.run(main())
