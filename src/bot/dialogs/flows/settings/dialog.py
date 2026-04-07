from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Group,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const

from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.widgets import BACK_BUTTON, MAIN_MENU_BUTTON
from bot.dialogs.flows.settings.states import SettingsSG

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
                SwitchTo(
                    text=Const('Юзеры'),
                    id='users',
                    state=SettingsSG.users,
                ),
            ),
            MAIN_MENU_BUTTON,
        ),
        state=SettingsSG.start,
    ),
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
                    state=SettingsSG.add_user,
                ),
                Button(
                    text=Const('Удалить юзера'),
                    id='remove_user',
                    on_click=on_click_in_dev,
                ),
            ),
            BACK_BUTTON,
            MAIN_MENU_BUTTON,
        ),
        state=SettingsSG.users,
    ),
)
