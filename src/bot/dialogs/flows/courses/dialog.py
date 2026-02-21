from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.common.getters import get_tg_username
from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.widgets import MAIN_MENU_BUTTON
from bot.dialogs.flows.courses.states import CoursesSG

courses_dialog = Dialog(
    Window(
        Format(text='===  Меню Курсы  ==='),
        Group(
            Row(
                Button(
                    text=Const('Добавить курс'),
                    id='add_mentor',
                    on_click=on_click_in_dev,
                ),
                Button(
                    text=Const('Удалить курс'),
                    id='remove_mentor',
                    on_click=on_click_in_dev,
                ),
            ),
            Button(
                text=Const('Список курсов'),
                id='mentors_list',
                on_click=on_click_in_dev,
            ),
            MAIN_MENU_BUTTON,
        ),
        state=CoursesSG.start,
    )
)
