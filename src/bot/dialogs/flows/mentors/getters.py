import logging

from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import inject

logger = logging.getLogger(__name__)


@inject
async def get_stepik_username(
    dialog_manager: DialogManager,
    event_from_user: User, **_kwargs
) -> dict[str, Any]:
    username = dialog_manager.dialog_data.get('stepik_username')
    return {'stepik_username': username}
