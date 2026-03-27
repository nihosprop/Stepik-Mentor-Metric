import logging

from taskiq import TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq_pg.psycopg import PsycopgScheduleSource

from core.main_config import main_config

from .broker import broker
from .tasks import STATIC_TASKS

logger = logging.getLogger(__name__)
dsn = (
    f'postgresql://{main_config.postgres.user}:'
    f'{main_config.postgres.password.get_secret_value()}@'
    f'{main_config.postgres.host}:{main_config.postgres.port}/'
    f'{main_config.postgres.name}'
)
scheduler_source = PsycopgScheduleSource(
    dsn=dsn,
    broker=broker,
)
scheduler = TaskiqScheduler(broker=broker, sources=[scheduler_source])

logger.info('TaskIQ scheduler initialized')
logger.info(f'Found {len(STATIC_TASKS)} static tasks')


@broker.on_event(TaskiqEvents.CLIENT_STARTUP)
async def sync_static_schedules(_state: TaskiqState) -> None:
    logger.info('Syncing static tasks with PostgreSQL...')

    try:
        existing_schedules = await scheduler_source.get_schedules()
        logger.info(f'Found {len(existing_schedules)} schedules')
        existing_ids = {s.schedule_id for s in existing_schedules}

        for task in STATIC_TASKS:
            if task.schedule_id not in existing_ids:
                logger.info(f'Adding new static task to DB: {task.task_name}')
                await scheduler_source.add_schedule(task)
            else:
                logger.debug(f'Task {task.task_name} already registered.')

    except Exception as e:
        logger.error(f'Failed to sync schedules: {e}')
