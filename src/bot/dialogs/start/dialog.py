from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.start.getters import get_pars_mode
from bot.dialogs.start.handlers import in_dev
from bot.dialogs.start.states import StartSG

start_dialog = Dialog(
    Window(
        Format(text='Hello {user_name}!'),
        Button(text=Const('Менторы'), id='mentors', on_click=in_dev),
        Button(text=Const('Статистика'), id='statistic',on_click=in_dev),
        Button(text=Const('Курсы'), id='courses', on_click=in_dev),

        state=StartSG.start,
        getter=get_pars_mode,
    )
)
