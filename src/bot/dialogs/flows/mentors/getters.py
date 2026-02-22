import logging

from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import inject
from dishka.integrations.aiogram_dialog import FromDishka

from db.models import StepikUser
from db.repository.stepik_user_repo import StepikUserRepo

logger = logging.getLogger(__name__)


@inject
async def get_stepik_username(
    dialog_manager: DialogManager, event_from_user: User, **_kwargs
) -> dict[str, Any]:
    return {
        'stepik_username': dialog_manager.dialog_data.get('stepik_username')
    }


@inject
async def get_mentors_list(
    dialog_manager: DialogManager,
    event_from_user: User,
    stepik_user_repo: FromDishka[StepikUserRepo],
    **_kwargs,
) -> dict[str, list[StepikUser] | int]:
    mentors = await stepik_user_repo.get_all_mentors()
    return {'mentors': mentors, 'count': len(mentors)}
