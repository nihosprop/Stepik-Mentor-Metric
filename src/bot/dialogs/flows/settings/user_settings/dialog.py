import logging

from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Group,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.common.handlers import on_click_in_dev
from bot.dialogs.common.validators import check_tg_user_id
from bot.dialogs.common.widgets import (
    BACK_BUTTON,
    CANCEL_BUTTON,
    MAIN_MENU_BUTTON,
)
from bot.dialogs.flows.settings.user_settings.getters import get_user_tg_id
from bot.dialogs.flows.settings.user_settings.handlers import (
    add_visitor_rights,
    correct_tg_user_id,
    error_tg_user_id,
    no_text,
)
from bot.dialogs.flows.settings.user_settings.states import VisitorSettingsSG

logger = logging.getLogger(__name__)

user_settings = Dialog(
    Window(
        Const(
            text='<b>===  Настройки Визитёров  ===</b>\n\n'
            '<code>Визитёры бота могут только просматривать '
            'статистику.\nДля более широких прав, сделайте '
            'юзера администратором.</code>'
        ),
        Group(
            Row(
                SwitchTo(
                    text=Const('Добавить визитёра'),
                    id='add_user',
                    state=VisitorSettingsSG.add_rights,
                ),
                SwitchTo(
                    text=Const('Удалить визитёра'),
                    id='remove_user',
                    state=VisitorSettingsSG.remove_rights,
                    on_click=on_click_in_dev,
                ),
            ),
            SwitchTo(
                text=Const('Список визитёров'),
                id='mentors_list',
                state=VisitorSettingsSG.list_visitors,
                on_click=on_click_in_dev,
            ),
            CANCEL_BUTTON,
            MAIN_MENU_BUTTON,
        ),
        state=VisitorSettingsSG.start,
    ),
    Window(
        Const(
            text='<b>Отправьте Telegram-ID юзера.</b>\n\n'
            '<code>ID юзера можно получить у бота,'
            ' отправив ему дескриптор юзера: @имя</code>\n\n'
            '<a href="https://t.me/username_to_id_bot">IDBot</a>'
        ),
        TextInput(
            id='fill_user_id',
            type_factory=check_tg_user_id,
            on_success=correct_tg_user_id,
            on_error=error_tg_user_id,
        ),
        MessageInput(func=no_text, content_types=ContentType.ANY),
        BACK_BUTTON,
        MAIN_MENU_BUTTON,
        state=VisitorSettingsSG.add_rights,
    ),
    Window(
        Format('Подтвердите выдачу юзеру <b>{user_tg_id}</b> прав `Визитёр`'),
        Back(
            text=Const(text='✅ Подтвердить'),
            id='conf_rights',
            on_click=add_visitor_rights,  # ty: ignore[invalid-argument-type]
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        getter=get_user_tg_id,
        state=VisitorSettingsSG.confirm_rights,
    ),
)
