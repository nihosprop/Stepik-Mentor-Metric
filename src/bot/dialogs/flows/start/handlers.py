import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka

from db.repository.tg_user_repo import TGUserRepository

from .states import StartSG
from ..mentors.states import MentorSG

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

async def switch_to_mentors(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    logger.debug('Entry')

    await dialog_manager.start(state=MentorSG.start)

    logger.debug('Exit')


async def in_dev(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    **_kwargs,
) -> None:
    logger.debug('Entry')

    await clbk.answer('Кнопка в разработке!', show_alert=True)
    logger.debug('')

    logger.debug('Exit')
