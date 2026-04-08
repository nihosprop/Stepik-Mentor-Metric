import logging

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Group,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const

from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.widgets import CANCEL_BUTTON, MAIN_MENU_BUTTON
from bot.dialogs.flows.settings.user_settings.states import UserSettingsSG

logger = logging.getLogger(__name__)

user_settings = Dialog(
    Window(
        Const(
            text='<b>===  Настройки Юзеров  ===</b>\n\n'
            '<code>Юзеры бота могут только просматривать '
            'статистику.\nДля более широких прав, сделайте '
            'юзера администратором.</code>'
        ),
        Group(
            Row(
                SwitchTo(
                    text=Const('Добавить юзера'),
                    id='add_user',
                    state=UserSettingsSG.add_user,
                ),
                SwitchTo(
                    text=Const('Удалить юзера'),
                    id='remove_user',
                    state=UserSettingsSG.remove_user,
                    on_click=on_click_in_dev,
                ),
            ),
            CANCEL_BUTTON,
            MAIN_MENU_BUTTON,
        ),
        state=UserSettingsSG.start,
    ),
)
