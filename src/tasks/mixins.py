import uuid

from typing import Any

from taskiq.scheduler.scheduled_task.v2 import ScheduledTask


class MyScheduledTask(ScheduledTask):
    schedule_id: str = uuid.uuid4().hex
    labels: dict[str, Any] = {}
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
