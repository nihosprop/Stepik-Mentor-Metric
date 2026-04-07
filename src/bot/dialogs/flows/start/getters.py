import logging

from aiogram_dialog import DialogManager

logger = logging.getLogger(__name__)


async def get_access_flags(dialog_manager: DialogManager, **_kwargs) -> dict:
    """Passes permission flags from middleware to the window context."""
    is_admin_middleware_data = dialog_manager.middleware_data.get(
        'is_admin', False
    )
    logger.debug(f'{is_admin_middleware_data=}')
    return {'is_admin': is_admin_middleware_data}
