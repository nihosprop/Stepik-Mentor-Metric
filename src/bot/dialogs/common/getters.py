import logging

from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager

logger = logging.getLogger(__name__)


async def get_tg_username(event_from_user: User, **_kwargs) -> dict[str, Any]:
    """
    Given a User object, returns a dictionary containing the username.

    Args:
        event_from_user (aiogram.types.User):
         The User object containing user information.

    Returns:
        dict: A dictionary containing the user's username.
            The dictionary has a single key-value pair:
            - 'user_name' (str): The username of the user.
            If the user's username is empty,the username is set to 'Anonymous'.
            If the user's first name is not empty,
             the username is set to the first name.
    """
    username = 'Anonymous'
    if event_from_user.username and event_from_user.username.strip():
        username = f'@{event_from_user.username.strip()}'

    elif event_from_user.first_name and event_from_user.first_name.strip():
        username = event_from_user.first_name.strip()
    return {'user_name': username}


async def get_access_flags(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    """
    Retrieves permission flags from the middleware and
     passes them to the window context.

    Args:
        dialog_manager (aiogram_dialog.DialogManager):
         The DialogManager object for the current dialog.

    Returns:
        dict: A dictionary containing the permission flags.
            The dictionary has a single key-value pair:
            - 'role' (bool): The permission flags obtained from the middleware.
    """
    role = dialog_manager.middleware_data.get('role', False)
    logger.debug(f'{role=}')
    return {'role': role}


async def get_user_tg_id(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    """
    Getter function for the dialog window to display user_tg_id.

    Args:
        dialog_manager (aiogram_dialog.DialogManager):
         The DialogManager object for the current dialog.

    Returns:
        dict: A dictionary containing the user_tg_id.
            The dictionary has a single key-value pair:
            - 'user_tg_id' (str):
             The user_tg_id obtained from the dialog manager.
    """
    return {'user_tg_id': dialog_manager.dialog_data.get('user_tg_id', '')}
