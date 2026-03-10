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

from bot.dialogs.common.getters import get_tg_username
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
    on_delete_mentor,
    on_mentor_selected,
)
from bot.dialogs.flows.statistic.states import StatisticSG

statistic_dialog = Dialog(
    Window(
        Format(text='===  Меню Статистики  ==='),
        SwitchTo(
            text=Const('Общая'),
            id='general_stat',
            state=StatisticSG.general
        ),
        SwitchTo(
            text=Const('Индивидуальная'),
            id='individual',
            state=StatisticSG.individual),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        state=StatisticSG.start)
    )
