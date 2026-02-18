from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.flows.start.getters import get_tg_username
from bot.dialogs.flows.start.handlers import in_dev
from bot.dialogs.flows.start.states import StartSG

start_dialog = Dialog(
    Window(
        Format(text='Привет {user_name}!\n===  Главное меню  ==='),
        Group(
            Row(
                Button(text=Const('Менторы'), id='mentors', on_click=in_dev),
                Button(text=Const('Курсы'), id='courses', on_click=in_dev),
            ),
            Button(text=Const('Статистика'), id='statistic', on_click=in_dev),
        ),
        getter=get_tg_username,
        state=StartSG.start,
    )
)
