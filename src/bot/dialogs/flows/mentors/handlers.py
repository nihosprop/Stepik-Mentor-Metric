import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.flows.start.states import StartSG

mentor_router = Router()

logger = logging.getLogger(__name__)


async def switch_to_main_menu(
    _clbk: CallbackQuery, _button: Button, dialog_manager: DialogManager
) -> None:
    logger.debug('Entry')

    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)

    logger.debug('Exit')
