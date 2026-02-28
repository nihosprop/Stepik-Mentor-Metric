import logging

from taskiq import TaskiqEvents, TaskiqState

from tasks.tasks import test_ping_admin

from .broker import broker
from .mixins import MyScheduledTask
from .scheduler import scheduler_source

logger = logging.getLogger(__name__)


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
