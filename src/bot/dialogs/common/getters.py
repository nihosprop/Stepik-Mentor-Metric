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
    is_admin_middleware_data = dialog_manager.middleware_data.get(
        'is_admin', False
    )
    logger.debug(f'{is_admin_middleware_data=}')
    return {'is_admin': is_admin_middleware_data}