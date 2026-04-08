import logging

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Group,
    Row,
    Start,
)
from aiogram_dialog.widgets.text import Const

from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.widgets import MAIN_MENU_BUTTON
from bot.dialogs.flows.settings.states import SettingsSG
from bot.dialogs.flows.settings.user_settings.states import UserSettingsSG

logger = logging.getLogger(__name__)

settings_dialog = Dialog(
    Window(
        Const(text='<b>===  Меню Настроек  ===</b>'),
        Group(
            Row(
                Button(
                    text=Const('Админы'),
                    id='admins',
                    on_click=on_click_in_dev,
                ),
                Start(
                    text=Const('Юзеры'),
                    id='users',
                    state=UserSettingsSG.start,
                ),
            ),
            MAIN_MENU_BUTTON,
        ),
        state=SettingsSG.start,
    ),
)
