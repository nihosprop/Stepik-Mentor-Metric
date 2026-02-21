import logging

from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import inject

logger = logging.getLogger(__name__)




@inject
async def get_tg_username(event_from_user: User, **_kwargs
) -> dict[str, Any]:

    username = 'Anonymous'
    if event_from_user.username and event_from_user.username.strip():
        username = f'@{event_from_user.username.strip()}'

    elif event_from_user.first_name and event_from_user.first_name.strip():
        username = event_from_user.first_name.strip()
    return {'user_name': username}