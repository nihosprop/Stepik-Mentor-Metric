from aiogram_dialog.widgets.kbd import Button, Back
from aiogram_dialog.widgets.text import Const

from .handlers import switch_to_main_menu

MAIN_MENU_BUTTON = Button(
    text=Const('☰ В главное меню'),
    id='in_main_menu',
    on_click=switch_to_main_menu,
)

BACK_BUTTON = Back(Const('◀️ Назад'), id='back')