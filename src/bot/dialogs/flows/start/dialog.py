from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row, Start
from aiogram_dialog.widgets.text import Const

from bot.dialogs.common.getters import get_tg_username
from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.flows.start.handlers import (
    switch_to_courses,
    switch_to_mentors,
)
from bot.dialogs.flows.start.states import StartSG
from bot.dialogs.flows.statistic.states import StatisticSG

# TODO: change to Start()
start_dialog = Dialog(
    Window(
        Const(text='===  Главное меню  ==='),
        Group(
            Row(
                Button(
                    text=Const('Менторы'),
                    id='mentors',
                    on_click=switch_to_mentors,
                ),
                Button(
                    text=Const('Курсы'),
                    id='courses',
                    on_click=switch_to_courses,
                ),
            ),
            Start(
                text=Const('Статистика'),
                id='statistic',
                state=StatisticSG.start,
            ),
            Button(
                text=Const('Настройки'),
                id='settings',
                on_click=on_click_in_dev,
            ),
        ),
        getter=get_tg_username,
        state=StartSG.start,
    )
)
