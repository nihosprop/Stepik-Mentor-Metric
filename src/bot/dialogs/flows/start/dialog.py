from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Group, Row, Start
from aiogram_dialog.widgets.text import Const

from bot.dialogs.common.getters import get_tg_username
from bot.dialogs.flows.courses.states import CoursesSG
from bot.dialogs.flows.mentors.states import MentorSG
from bot.dialogs.flows.settings.states import SettingsSG
from bot.dialogs.flows.start.states import StartSG
from bot.dialogs.flows.statistic.states import StatisticSG

# TODO: change to Start()
start_dialog = Dialog(
    Window(
        Const(text='===  Главное меню  ==='),
        Group(
            Row(
                Start(
                    text=Const('Менторы'),
                    id='mentors',
                    state=MentorSG.start,
                ),
                Start(
                    text=Const('Курсы'),
                    id='courses',
                    state=CoursesSG.start,
                ),
            ),
            Start(
                text=Const('Статистика'),
                id='statistic',
                state=StatisticSG.start,
            ),
            Start(
                text=Const('Настройки'),
                id='settings',
                state=SettingsSG.start,
            ),
        ),
        getter=get_tg_username,
        state=StartSG.start,
    ),
    name='start'
)
