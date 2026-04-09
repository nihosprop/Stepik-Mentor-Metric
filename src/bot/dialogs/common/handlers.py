import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.flows.start.states import StartSG

logger = logging.getLogger(__name__)


async def switch_to_main_menu(
    _clbk: CallbackQuery, _button: Button, dialog_manager: DialogManager
) -> None:
    logger.debug('Entry')

    await dialog_manager.start(
        state=StartSG.start,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT,
    )

    logger.debug('Exit')


async def on_click_in_dev(
    clbk: CallbackQuery,
    _button: Button,
    _dialog_manager: DialogManager,
    **_kwargs,
) -> None:
    logger.debug('Entry')
    await clbk.answer('Кнопка в разработке 🛠️', show_alert=True)
    logger.debug('Exit')
