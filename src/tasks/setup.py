import logging

from taskiq import TaskiqEvents, TaskiqState

from .broker import broker
from .scheduler import scheduler_source
from .tasks import STATIC_TASKS

logger = logging.getLogger(__name__)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def setup_schedules(_state: TaskiqState) -> None:
    logger.info('Setting up schedules...')
    await scheduler_source.startup()

    existing_schedules = await scheduler_source.get_schedules()
    existing_ids = {s.schedule_id for s in existing_schedules}

    for task in STATIC_TASKS:
        if task.schedule_id not in existing_ids:
            await scheduler_source.add_schedule(task)
            logger.info(f'Schedule added for {task.task_name}')
        else:
            logger.info(f'Task {task.task_name} already in DB')
