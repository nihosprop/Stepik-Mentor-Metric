from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Group, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.common.getters import get_tg_username
from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.validators import check_stepik_profile_link
from bot.dialogs.common.widgets import BACK_BUTTON, MAIN_MENU_BUTTON
from bot.dialogs.flows.mentors.getters import get_stepik_username
from bot.dialogs.flows.mentors.handlers import (
    correct_link_to_mentor,
    error_link_to_mentor,
)
from bot.dialogs.flows.mentors.states import MentorSG

mentors_dialog = Dialog(
    Window(
        Format(text='===  Меню Менторов  ==='),
        Group(
            Row(
                SwitchTo(
                    text=Const('Добавить ментора'),
                    id='add_mentor',
                    state=MentorSG.fill_link_to_mentor,
                ),
                Button(
                    text=Const('Удалить ментора'),
                    id='remove_mentor',
                    on_click=on_click_in_dev,
                ),
            ),
            Button(
                text=Const('Список менторов'),
                id='mentors_list',
                on_click=on_click_in_dev,
            ),
            MAIN_MENU_BUTTON,
        ),
        getter=get_tg_username,
        state=MentorSG.start,
    ),
    Window(
        Const(text='Отправьте ссылку на профиль ментора'),
        TextInput(
            id='fill_link_mentor',
            type_factory=check_stepik_profile_link,
            on_success=correct_link_to_mentor,
            on_error=error_link_to_mentor,
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        state=MentorSG.fill_link_to_mentor,
    ),
    Window(
        Format('Подтвердите добавление Ментора:\n<b>{stepik_username}</b>'),
        Button(
            Const(text='✅ Подтвердить'),
            id='confirm_mentor',
            on_click=on_click_in_dev,
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        getter=get_stepik_username,
        state=MentorSG.confirm_mentor,
    ),
)
