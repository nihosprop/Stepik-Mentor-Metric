from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.start.getters import get_pars_mode
from bot.dialogs.start.handlers import on_help
from bot.dialogs.start.states import StartSG

start_dialog = Dialog(
    Window(
        Format(text='Hello {user_name}!\nYour mode: {pars_mode}!'),
        Button(text=Const('Помощь)'), id='help',
               on_click=on_help),
        state=StartSG.start,
        getter=get_pars_mode,
    )
)
