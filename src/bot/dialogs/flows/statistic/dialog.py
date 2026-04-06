from aiogram_dialog import Dialog, ShowMode, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const

from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.widgets import BACK_BUTTON, MAIN_MENU_BUTTON
from bot.dialogs.flows.statistic.handlers import (
    send_current_month_detailed_stats,
    send_last_month_detailed_stats,
    send_last_month_general_stats,
    sent_current_month_general_report,
)
from bot.dialogs.flows.statistic.states import StatisticSG

statistic_dialog = Dialog(
    Window(
        Const(text='===  Меню Статистики  ==='),
        SwitchTo(
            text=Const('Общая'), id='general_stat', state=StatisticSG.general
        ),
        Button(
            text=Const('Индивидуальная'),
            id='individual',
            on_click=on_click_in_dev,
        ),
        MAIN_MENU_BUTTON,
        state=StatisticSG.start,
    ),
    Window(
        Const('Выберите период ⤵️'),
        SwitchTo(
            text=Const('Общая (Текущий месяц)'),
            id='general_stats_current',
            on_click=sent_current_month_general_report,  # ty:ignore[invalid-argument-type]
            state=StatisticSG.general,
            show_mode=ShowMode.DELETE_AND_SEND,
        ),
        SwitchTo(
            text=Const('Общая (Прошедший месяц)'),
            id='general_stats_last',
            on_click=send_last_month_general_stats,  # ty:ignore[invalid-argument-type]
            state=StatisticSG.general,
            show_mode=ShowMode.DELETE_AND_SEND,
        ),
        Button(
            text=Const('Подробная (Текущий месяц)'),
            id='curr_month',
            on_click=send_current_month_detailed_stats,  # ty:ignore[invalid-argument-type]
        ),
        Button(
            text=Const('Подробная (Прошедший месяц)'),
            id='last_month',
            on_click=send_last_month_detailed_stats,  # ty:ignore[invalid-argument-type]
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
