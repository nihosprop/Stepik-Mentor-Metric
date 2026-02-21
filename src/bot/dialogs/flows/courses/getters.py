from infrastructure.stepik.client import StepikAPIClient
from dishka.integrations.aiogram_dialog import FromDishka
import logging

from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import inject

logger = logging.getLogger(__name__)

@inject
async def get_course_title(
    dialog_manager: DialogManager, event_from_user: User, **_kwargs
) -> dict[str, Any]:
    return {
        'course_title': dialog_manager.dialog_data.get('course_title')
    }