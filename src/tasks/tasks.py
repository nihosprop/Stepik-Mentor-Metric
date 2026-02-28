import logging

from aiogram import Bot
from dishka.integrations.taskiq import FromDishka, inject

from core.main_config import Config

from .broker import broker
from .mixins import MyScheduledTask

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


STATIC_TASKS = [
    MyScheduledTask(
        task_name=test_ping_admin.task_name,
        schedule_id='1f779070-5683-4d6e-bc51-3e5e95175564',
        cron='* * * * *',
    )
]
