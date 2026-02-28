import logging

from aiogram import Bot
from dishka.integrations.taskiq import FromDishka, inject

from core.main_config import Config

from .broker import broker

logger = logging.getLogger(__name__)


@broker.task
@inject(patch_module=True)
async def test_ping_admin(
    bot: FromDishka[Bot],
    config: FromDishka[Config],
) -> None:
    try:
        logger.info('Send ping admin message')
        admin_id = config.bot.admins[0]
        await bot.send_message(chat_id=admin_id, text='Ping')
    except Exception as e:
        logger.error('Error in task test_ping_admin')
        raise e
