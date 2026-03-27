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
    """
    Автоматическая синхронизация задач при старте планировщика.
    Гарантирует заполнение базы расписаниями сразу после down -v.
    """
    logger.info('Syncing static tasks with PostgreSQL...')

    # ПРИМЕЧАНИЕ: Мы НЕ вызываем scheduler_source.startup() здесь,
    # так как планировщик TaskIQ CLI сам вызывает его перед этим событием.

    try:
        # 1. Получаем список того, что уже есть в БД
        existing_schedules = await scheduler_source.get_schedules()
        logger.info(f'Found {len(existing_schedules)} schedules')
        existing_ids = {s.schedule_id for s in existing_schedules}

        # 2. Проходим по эталонному списку из кода (tasks.py)
        for task in STATIC_TASKS:
            if task.schedule_id not in existing_ids:
                logger.info(f'Adding new static task to DB: {task.task_name}')
                # Используем метод add_schedule у объекта источника
                await scheduler_source.add_schedule(task)
            else:
                logger.debug(f'Task {task.task_name} already registered.')

    except Exception as e:
        logger.error(f'Failed to sync schedules: {e}')


# async def setup_schedules() -> None:
#     """Setup schedules."""
#     logger.info('Setting up schedules in scheduler...')
# await scheduler_source.startup()
# try:
#     existing_schedules = await scheduler_source.get_schedules()
#     existing_ids = {s.schedule_id for s in existing_schedules}
#     logger.info(f'Existing schedules: {existing_ids}')
#
#     if not STATIC_TASKS:
#         logger.info('No static tasks to add.')
#         return
#
#     for task in STATIC_TASKS:
#         if task.schedule_id not in existing_ids:
#             await scheduler_source.add_schedule(task)
#             logger.info(f'Schedule added for {task.task_name}')
#         else:
#             logger.info(f'Task {task.task_name} already in DB')
# except Exception as e:
#     logger.error(f'Failed to setup schedules: {e}', exc_info=True)


# asyncio.create_task(setup_schedules())
