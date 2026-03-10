from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const

from bot.dialogs.common.widgets import BACK_BUTTON, MAIN_MENU_BUTTON
from bot.dialogs.flows.statistic.handlers import (
    send_current_month,
    send_last_month,
)
from bot.dialogs.flows.statistic.states import StatisticSG

statistic_dialog = Dialog(
    Window(
        Const(text='===  Меню Статистики  ==='),
        SwitchTo(
            text=Const('Общая'), id='general_stat', state=StatisticSG.general
        ),
        SwitchTo(
            text=Const('Индивидуальная'),
            id='individual',
            state=StatisticSG.individual,
        ),
        MAIN_MENU_BUTTON,
        state=StatisticSG.start,
    ),
    Window(
        Const('Выберите отчет'),
        Button(
            text=Const('За текущий месяц'),
            id='curr_month',
            on_click=send_current_month,  # type: ignore[arg-type]
        ),
        Button(
            text=Const('За прошедший месяц'),
            id='last_month',
            on_click=send_last_month,  # type: ignore[arg-type]
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        state=StatisticSG.general,
    ),
    Window(
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        state=StatisticSG.individual,
    ),
)
