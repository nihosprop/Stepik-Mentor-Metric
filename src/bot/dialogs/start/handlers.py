import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka

from db.repository.user_repo import UserRepository

from .states import StartSG

start_router = Router()

logger = logging.getLogger(__name__)


@start_router.message(CommandStart())
async def start(
    msg: Message,
    dialog_manager: DialogManager,
    user_repo: FromDishka[UserRepository]
) -> None:
    logger.debug('Entry')

    if msg.from_user:
        await user_repo.add_if_not_exists(telegram_user=msg.from_user)
        await dialog_manager.start(
            state=StartSG.start,
            mode=StartMode.RESET_STACK)
        await msg.delete()
        return

    logger.warning('Failed to determine user')
    logger.debug('Exit')


async def on_help(
    clbk: CallbackQuery, _button: Button, dialog_manager: DialogManager,
        **_kwargs
) -> None:
    logger.debug('Entry')

    await clbk.answer('Помощь скоро будет!', show_alert=True)

    logger.debug('Exit')
