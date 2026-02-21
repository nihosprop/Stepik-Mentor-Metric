from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Group, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.validators import check_stepik_course_link
from bot.dialogs.common.widgets import BACK_BUTTON, MAIN_MENU_BUTTON
from bot.dialogs.flows.courses.getters import get_course_title
from bot.dialogs.flows.courses.handlers import (
    add_course_to_db,
    correct_link_to_course,
    error_link_to_course,
)
from bot.dialogs.flows.courses.states import CoursesSG

courses_dialog = Dialog(
    Window(
        Format(text='===  Меню Курсы  ==='),
        Group(
            Row(
                SwitchTo(
                    text=Const('Добавить курс'),
                    id='add_mentor',
                    state=CoursesSG.fill_link_to_course,
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
    ),
    Window(
        Const(text='Отправьте ссылку на профиль ментора'),
        TextInput(
            id='link_course',
            type_factory=check_stepik_course_link,
            on_success=correct_link_to_course,
            on_error=error_link_to_course,
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        state=CoursesSG.fill_link_to_course,
    ),
    Window(
        Format('Подтвердите добавление Курса:\n<b>{course_title}</b>'),
        Back(
            text=Const(text='✅ Подтвердить'),
            id='confirm_curse',
            on_click=add_course_to_db,  # type: ignore[arg-type]
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        getter=get_course_title,
        state=CoursesSG.confirm_curse,
    ),
)
