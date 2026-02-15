import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka

from common.telegram_utils import get_username
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

    if tg_user := msg.from_user:
        await user_repo.upsert_user(telegram_user=tg_user)
        await dialog_manager.start(
            state=StartSG.start, mode=StartMode.RESET_STACK
        )
        await msg.delete()
        return

    logger.warning('Failed to determine user')
    logger.debug('Exit')


async def on_help(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    **_kwargs,
) -> None:
    """
    Handle help button callback.

    Sends an alert answer to the user indicating that help
     will be provided soon.

    Args:
        clbk (CallbackQuery): The callback query from the pressed help button.
        _button (Button): The pressed button widget (unused).
        dialog_manager (DialogManager): Dialog manager instance (unused here).
        **_kwargs: Additional keyword arguments forwarded by aiogram-dialog.

    Returns:
        None
    """
    logger.debug('Entry')

    await clbk.answer(
        f'{get_username(clbk)}, Помощь скоро будет!', show_alert=True
    )

    logger.debug('Exit')
