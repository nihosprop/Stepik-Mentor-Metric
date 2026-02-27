import logging

from aiogram import Bot
from dishka.integrations.taskiq import FromDishka, inject
from taskiq import TaskiqEvents, TaskiqState

from core.main_config import Config

from .broker import broker
from .mixins import MyScheduledTask
from .scheduled import scheduler_source

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


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def setup_schedules(_state: TaskiqState) -> None:
    logger.info('Setting up schedules...')

    await scheduler_source.startup()

    task = MyScheduledTask(
        task_name=test_ping_admin.task_name,
        cron='* * * * *',
    )
    await scheduler_source.add_schedule(task)

    logger.info('Schedule added for test_ping_admin')
