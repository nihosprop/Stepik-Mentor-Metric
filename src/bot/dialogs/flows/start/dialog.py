from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.common.getters import get_tg_username
from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.flows.start.handlers import (
    switch_to_courses,
    switch_to_mentors,
)
from bot.dialogs.flows.start.states import StartSG

start_dialog = Dialog(
    Window(
        Format(text='===  Главное меню  ==='),
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
            Button(
                text=Const('Статистика'),
                id='statistic',
                on_click=on_click_in_dev,
            ),
        ),
        getter=get_tg_username,
        state=StartSG.start,
    )
)
