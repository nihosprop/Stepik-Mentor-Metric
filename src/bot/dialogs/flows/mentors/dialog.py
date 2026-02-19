from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.widgets import MAIN_MENU_BUTTON
from bot.dialogs.flows.mentors.states import MentorSG
from bot.dialogs.flows.start.getters import get_tg_username

mentors_dialog = Dialog(
    Window(
        Format(text='===  Меню Менторов  ==='),
        Group(
            Row(
                Button(
                    text=Const('Добавить ментора'),
                    id='add_mentor',
                    on_click=on_click_in_dev,
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
            MAIN_MENU_BUTTON
        ),
        getter=get_tg_username,
        state=MentorSG.start,
    )
)
