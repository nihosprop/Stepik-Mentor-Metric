import logging

from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager, ShowMode, StartMode

from ..flows.start.states import StartSG

logger = logging.getLogger(__name__)


async def on_unknown_state(
    event: ErrorEvent, dialog_manager: DialogManager
) -> None:
    """
    Handle an unknown state error in a dialog.

    This function catches errors of type ErrorEvent and tries to reset the
     dialog stack. If successful, it logs the reset and returns.
      If unsuccessful, it logs the error and returns.

    Args:
        event (ErrorEvent): The event that triggered the error.
        dialog_manager (DialogManager): The dialog manager to reset the stack.
    Returns:
        None
    """
    logger.error(
        f'Caught error type: {type(event.exception)}: {event.exception}'
    )
    clbk = event.update.callback_query
    msg = event.update.message

    if not clbk and not msg:
        logger.debug('Exit: callback and message not found')
        return

    logger.error('Restarting dialog due to state error: %s', event.exception)

    try:
        await dialog_manager.start(
            state=StartSG.start,
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
        logger.info('Dialog stack reset successfully')
    except Exception as e:
        logger.error(f'Could not reset dialog stack: {e}')
