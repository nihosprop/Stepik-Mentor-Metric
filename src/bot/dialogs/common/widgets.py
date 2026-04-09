from aiogram.enums import ButtonStyle
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.style import Style
from aiogram_dialog.widgets.text import Const

from .handlers import switch_to_main_menu

MAIN_MENU_BUTTON = Button(
    text=Const('☰ В главное меню'),
    id='in_main_menu',
    on_click=switch_to_main_menu,
    style=Style(ButtonStyle.PRIMARY),
)
BACK_BUTTON = Back(Const('◀️ Назад'), id='back')
CANCEL_BUTTON = Cancel(Const('◀️ Назад'), id='cancel')