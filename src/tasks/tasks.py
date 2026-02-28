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

    default_tasks = [
        MyScheduledTask(
            task_name=test_ping_admin.task_name,
            schedule_id='1f779070-5683-4d6e-bc51-3e5e95175564',
            cron='* * * * *',
        )
    ]
    existing_schedules = await scheduler_source.get_schedules()
    existing_ids = {s.schedule_id for s in existing_schedules}

    for task in default_tasks:
        if task.schedule_id not in existing_ids:
            await scheduler_source.add_schedule(task)
            logger.info(f'Schedule added for {task.task_name}')
        else:
            logger.info(f'Task {task.task_name} already in DB')
