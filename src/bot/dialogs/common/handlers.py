import logging

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
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


async def correct_tg_user_id(
    _msg: Message,
    _widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    logger.debug('Entry')

    dialog_manager.dialog_data['user_tg_id'] = text
    await dialog_manager.next()

    logger.debug('Exit')


async def error_tg_user_id(
    msg: Message,
    _widget: ManagedTextInput,
    _dialog_manager: DialogManager,
    _error: ValueError,
) -> None:
    logger.debug('Entry')

    await msg.delete()
    await msg.answer(
        text='Вы ввели некорректный ID юзера! Попробуйте еще раз.'
    )

    logger.debug('Exit')


async def no_text(
    msg: Message, _widget: MessageInput, _dialog_manager: DialogManager
) -> None:
    await msg.answer(text='Вы ввели не текст!', show_alert=True)
