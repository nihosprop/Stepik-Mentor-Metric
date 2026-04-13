import logging

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Group,
    Row,
    Start,
)
from aiogram_dialog.widgets.text import Const

from bot.dialogs.common.widgets import MAIN_MENU_BUTTON
from bot.dialogs.flows.settings.admin_settings.states import AdminSettingsSG
from bot.dialogs.flows.settings.states import SettingsSG
from bot.dialogs.flows.settings.visitor_settings.states import (
    VisitorSettingsSG,
)

logger = logging.getLogger(__name__)

settings_dialog = Dialog(
    Window(
        Const(text='<b>===  Меню Настроек  ===</b>'),
        Group(
            Row(
                Start(
                    text=Const('Админы'),
                    id='admins',
                    state=AdminSettingsSG.start,
                ),
                Start(
                    text=Const('Визитёры'),
                    id='visitors',
                    state=VisitorSettingsSG.start,
                ),
            ),
            MAIN_MENU_BUTTON,
        ),
        state=SettingsSG.start,
    ),
)
