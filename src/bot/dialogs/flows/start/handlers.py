import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode

from .states import StartSG

start_router = Router()

logger = logging.getLogger(__name__)


@start_router.message(CommandStart())
async def start(
    msg: Message,
    dialog_manager: DialogManager,
) -> None:
    """
    Handle the /start command.

    This handler upserts the Telegram user in the repository, starts the
    dialog at the StartSG.start state resetting the dialog stack, and
    deletes the incoming start message.

    Args:
        msg (Message): Incoming Telegram message that triggered /start.
        dialog_manager (DialogManager): Dialog manager to control dialogs.
         for user operations.

    Returns:
        None
    """
    logger.debug('Entry')
    await msg.delete()

    await dialog_manager.start(
        state=StartSG.start,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
    logger.debug('Exit')

    logger.warning('Failed to determine user')
    logger.debug('Exit')
