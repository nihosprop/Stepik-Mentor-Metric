from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Group,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.common.getters import get_tg_username
from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.validators import check_stepik_profile_link
from bot.dialogs.common.widgets import BACK_BUTTON, MAIN_MENU_BUTTON
from bot.dialogs.flows.mentors.getters import (
    get_mentors,
    get_stepik_username,
)
from bot.dialogs.flows.mentors.handlers import (
    add_mentor_to_db,
    correct_link_to_mentor,
    error_link_to_mentor,
    on_delete_mentor,
    on_mentor_selected,
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
                SwitchTo(
                    text=Const('Удалить ментора'),
                    id='remove_mentor',
                    state=MentorSG.selection_mentors,
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
        Back(
            text=Const(text='✅ Подтвердить'),
            id='confirm_mentor',
            on_click=add_mentor_to_db,  # type: ignore[arg-type]
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        getter=get_stepik_username,
        state=MentorSG.confirm_mentor,
    ),
    Window(
        # TODO: change the text based on the availability of mentors
        Format('Найдено менторов: {count}\nВыберите нужного:'),
        ScrollingGroup(
            Select(
                Format(text='{item.full_name}'),
                id='s_mentors',
                item_id_getter=lambda x: x.user_id,
                items='mentors',
                on_click=on_mentor_selected,  # type: ignore[arg-type]
            ),
            id='mentors_scroll',
            width=1,
            height=4,
        ),
        MAIN_MENU_BUTTON,
        SwitchTo(Const('Назад'), id='back', state=MentorSG.start),
        state=MentorSG.selection_mentors,
        getter=get_mentors,
    ),
    Window(
        Format(text='Подтвердите удаление!'),
        Back(
            text=Const(text='✅ Подтвердить'),
            id='conf_del_mentor',
            on_click=on_delete_mentor,  # type: ignore[arg-type]
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        getter=get_stepik_username,
        state=MentorSG.confirm_delete_mentor,
    ),
)
