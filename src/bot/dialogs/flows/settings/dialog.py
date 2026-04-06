from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.flows.settings.states import SettingsSG
from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Group,
    NextPage,
    PrevPage,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
    Button,
)
from aiogram_dialog.widgets.text import Const, Format, List

from bot.dialogs.common.validators import check_stepik_profile_link
from bot.dialogs.common.widgets import BACK_BUTTON, MAIN_MENU_BUTTON
from bot.dialogs.flows.mentors.getters import (
    get_list_mentors,
    get_mentors,
    get_stepik_username,
)
from bot.dialogs.flows.mentors.handlers import (
    add_mentor_to_db,
    correct_link_to_mentor,
    error_link_to_mentor,
    on_mentor_selected,
    on_remove_mentor_status,
)

settings_dialog = Dialog(
    Window(
        Const(text='===  Меню Настроек  ==='),
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
        Const(text='===  Настройки Юзеров  ==='),
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
            MAIN_MENU_BUTTON,
        ),
        state=SettingsSG.users,
    ),
)
