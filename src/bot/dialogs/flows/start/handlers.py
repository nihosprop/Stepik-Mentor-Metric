import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka.integrations.aiogram import FromDishka

from db.repository.tg_user_repo import TGUserRepository

from .states import StartSG

start_router = Router()

logger = logging.getLogger(__name__)


@start_router.message(CommandStart())
async def start(
    msg: Message,
    dialog_manager: DialogManager,
    user_repo: FromDishka[TGUserRepository],
) -> None:
    """
    Handle the /start command.

    This handler upserts the Telegram user in the repository, starts the
    dialog at the StartSG.start state resetting the dialog stack, and
    deletes the incoming start message.

    Args:
        msg (Message): Incoming Telegram message that triggered /start.
        dialog_manager (DialogManager): Dialog manager to control dialogs.
        user_repo (FromDishka[UserRepository]): Repository wrapper
         for user operations.

    Returns:
        None
    """
    logger.debug('Entry')
    await msg.delete()

    if tg_user := msg.from_user:
        await user_repo.upsert_user(telegram_user=tg_user)
        await dialog_manager.start(
            state=StartSG.start,
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
        logger.debug('Exit')
        return

    logger.warning('Failed to determine user')
    logger.debug('Exit')
