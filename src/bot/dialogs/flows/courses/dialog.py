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
)
from aiogram_dialog.widgets.text import Const, Format, List

from bot.dialogs.common.getters import get_access_flags
from bot.dialogs.common.validators import check_stepik_course_link
from bot.dialogs.common.widgets import BACK_BUTTON, MAIN_MENU_BUTTON
from bot.dialogs.flows.courses.getters import (
    get_course_title,
    get_courses,
    get_list_courses,
)
from bot.dialogs.flows.courses.handlers import (
    add_course_to_db,
    correct_link_to_course,
    error_link_to_course,
    on_course_selected,
    on_delete_course,
)
from bot.dialogs.flows.courses.states import CoursesSG

courses_dialog = Dialog(
    Window(
        Format(text='===  Меню Курсы  ==='),
        Group(
            Row(
                SwitchTo(
                    text=Const('Добавить курс'),
                    id='add_course',
                    state=CoursesSG.fill_link_to_course,
                    when=(F['role']).in_({'super_admin', 'admin'}),
                ),
                SwitchTo(
                    text=Const('Удалить курс'),
                    id='remove_course',
                    state=CoursesSG.selection_courses,
                    when=(F['role']).in_({'super_admin', 'admin'})
                ),
            ),
            SwitchTo(
                text=Const('Список курсов'),
                id='courses_list',
                state=CoursesSG.list_courses,
            ),
            MAIN_MENU_BUTTON,
        ),
        state=CoursesSG.start,
    ),
    Window(
        Const(text='Отправьте ссылку на курс'),
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
            on_click=add_course_to_db,  # ty:ignore[invalid-argument-type]
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        getter=get_course_title,
        state=CoursesSG.confirm_curse,
    ),
    Window(
        # TODO: change the text based on the availability of mentors
        Format('Найдено курсов: {count}\nВыберите нужный для удаления:'),
        ScrollingGroup(
            Select(
                Format(text='{item.title}'),
                id='s_course',
                item_id_getter=lambda x: x.course_id,
                items='courses',
                on_click=on_course_selected,  # ty:ignore[invalid-argument-type]
            ),
            id='courses_scroll',
            width=1,
            height=4,
            hide_pager=True,
        ),
        Row(
            PrevPage(
                scroll='courses_scroll',
                text=Format(text='{data[prev_page_button]}'),
            ),
            NextPage(
                scroll='courses_scroll',
                text=Format(text='{data[next_page_button]}'),
            ),
            when=F['count'] > 4,
        ),
        MAIN_MENU_BUTTON,
        SwitchTo(Const('◀️ Назад'), id='in_start_1', state=CoursesSG.start),
        state=CoursesSG.selection_courses,
        getter=get_courses,
    ),
    Window(
        Format(text='Подтвердите удаление!'),
        SwitchTo(
            text=Const(text='✅ Подтвердить'),
            id='conf_del_course',
            on_click=on_delete_course,  # ty:ignore[invalid-argument-type]
            state=CoursesSG.selection_courses,
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        getter=get_course_title,
        state=CoursesSG.confirm_delete_course,
    ),
    Window(
        Const(text='📚 Список отслеживаемых курсов:\n'),
        List(
            Format(text='{item}'),
            items='courses',
        ),
        MAIN_MENU_BUTTON,
        SwitchTo(Const('◀️ Назад'), id='in_start_2', state=CoursesSG.start),
        getter=get_list_courses,
        state=CoursesSG.list_courses,
        disable_web_page_preview=True,
    ),
    getter=get_access_flags,
)
