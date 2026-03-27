import logging

from taskiq import TaskiqScheduler
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
