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
from bot.dialogs.flows.mentors.states import MentorSG

mentors_dialog = Dialog(
    Window(
        Const(text='===  Меню Менторов  ==='),
        Group(
            Row(
                SwitchTo(
                    text=Const('Добавить ментора'),
                    id='add_mentor',
                    state=MentorSG.fill_link_to_mentor,
                ),
                SwitchTo(
                    text=Const('Удалить ментора'),
                    id='remove_mentor',
                    state=MentorSG.selection_mentors,
                    when='is_admin',
                ),
            ),
            SwitchTo(
                text=Const('Список менторов'),
                id='mentors_list',
                state=MentorSG.list_mentors,
            ),
            MAIN_MENU_BUTTON,
        ),
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
        Back(
            text=Const(text='✅ Подтвердить'),
            id='confirm_mentor',
            on_click=add_mentor_to_db,  # ty:ignore[invalid-argument-type]
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        getter=get_stepik_username,
        state=MentorSG.confirm_mentor,
    ),
    Window(
        # TODO: change the text based on the availability of mentors
        Format('Найдено менторов: {count}\nВыберите нужного для удаления:'),
        ScrollingGroup(
            Select(
                Format(text='{item.full_name}'),
                id='s_mentors',
                item_id_getter=lambda x: x.user_id,
                items='mentors',
                on_click=on_mentor_selected,  # ty:ignore[invalid-argument-type]
            ),
            id='mentors_scroll',
            width=1,
            height=4,
            hide_pager=True,
        ),
        Row(
            PrevPage(
                scroll='mentors_scroll',
                text=Format(text='{data[prev_page_button]}'),
            ),
            NextPage(
                scroll='mentors_scroll',
                text=Format(text='{data[next_page_button]}'),
            ),
            when=F['count'] > 4,
        ),
        MAIN_MENU_BUTTON,
        SwitchTo(Const('◀️ Назад'), id='in_start_1', state=MentorSG.start),
        state=MentorSG.selection_mentors,
        getter=get_mentors,
    ),
    Window(
        Format(text='Подтвердите удаление!'),
        SwitchTo(
            text=Const(text='✅ Подтвердить'),
            id='conf_del_mentor',
            on_click=on_remove_mentor_status,  # ty:ignore[invalid-argument-type]
            state=MentorSG.selection_mentors,
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        getter=get_stepik_username,
        state=MentorSG.confirm_delete_mentor,
    ),
    Window(
        Const(text='👥 Список менторов:\n'),
        List(
            Format(text='{item}'),
            items='mentors',
        ),
        MAIN_MENU_BUTTON,
        SwitchTo(Const('◀️ Назад'), id='in_start_2', state=MentorSG.start),
        getter=get_list_mentors,
        state=MentorSG.list_mentors,
        disable_web_page_preview=True,
    ),
    getter=get_access_flags,
)
