import logging

from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager

logger = logging.getLogger(__name__)


async def get_tg_username(event_from_user: User, **_kwargs
) -> dict[str, Any]:
    username = 'Anonymous'
    if event_from_user.username and event_from_user.username.strip():
        username = f'@{event_from_user.username.strip()}'

    elif event_from_user.first_name and event_from_user.first_name.strip():
        username = event_from_user.first_name.strip()
    return {'user_name': username}

async def get_access_flags(dialog_manager: DialogManager, **_kwargs) -> dict:
    """Passes permission flags from middleware to the window context."""
    role = dialog_manager.middleware_data.get(
        'role', False
    )
    logger.debug(f'{role=}')
    return {'role': role}

async def get_user_tg_id(dialog_manager: DialogManager, **_kwargs) -> dict:
    """
    Getter function for the dialog window to display user_tg_id.
    """
    return {'user_tg_id': dialog_manager.dialog_data.get('user_tg_id', '')}