import logging

from aiogram import Bot
from dishka.integrations.taskiq import FromDishka, inject
from taskiq import TaskiqScheduler
from taskiq_redis import ListRedisScheduleSource

from core.main_config import Config, main_config

from .broker import broker

logger = logging.getLogger(__name__)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[
        ListRedisScheduleSource(
            f'redis://{main_config.redis.host}:{main_config.redis.port}'
        )
    ],
)


@broker.task(schedule=[{'cron': '* * * * *'}])
@inject(patch_module=True)
async def send_scheduled_ping(
    bot: FromDishka[Bot],
    config: FromDishka[Config],
) -> None:
    logger.debug('send_scheduled_ping')
    """Test task: sending a notification to the admin."""
    if config.bot.admins:
        admin_id = config.bot.admins[0]
        await bot.send_message(
            chat_id=admin_id,
            text=f'🚀 Taskiq:'
            f' Проверка связи {config.stepik.stepik_client_id=}!'
            f' Я работаю по расписанию.',
        )
