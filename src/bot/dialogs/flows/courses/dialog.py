from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.common.handlers import in_dev
from bot.dialogs.common.widgets import MAIN_MENU_BUTTON
from bot.dialogs.flows.courses.states import CoursesSG
from bot.dialogs.flows.start.getters import get_tg_username

courses_dialog = Dialog(
    Window(
        Format(text='===  Меню Курсы  ==='),
        Group(
            Row(
                Button(
                    text=Const('Добавить курс'),
                    id='add_mentor',
                    on_click=in_dev,
                ),
                Button(
                    text=Const('Удалить курс'),
                    id='remove_mentor',
                    on_click=in_dev,
                ),
            ),
            Button(
                text=Const('Список курсов'),
                id='mentors_list',
                on_click=in_dev,
            ),
            MAIN_MENU_BUTTON,
        ),
        getter=get_tg_username,
        state=CoursesSG.start,
    )
)
