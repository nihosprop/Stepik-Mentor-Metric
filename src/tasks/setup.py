import logging

from taskiq import TaskiqEvents, TaskiqState

from .broker import broker
from .tasks import STATIC_TASKS

logger = logging.getLogger(__name__)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def setup_worker(_state: TaskiqState) -> None:
    logger.info('Worker started - ready to execute tasks')
    logger.info(f'Worker found {len(STATIC_TASKS)} static tasks')
