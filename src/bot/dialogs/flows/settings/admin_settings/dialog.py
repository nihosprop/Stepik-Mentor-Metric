import logging

from aiogram import F
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

from bot.dialogs.common.getters import get_access_flags, get_user_tg_id
from bot.dialogs.common.handlers import (
    correct_tg_user_id,
    error_tg_user_id,
    no_text,
    on_click_in_dev,
)
from bot.dialogs.common.validators import check_tg_user_id
from bot.dialogs.common.widgets import (
    BACK_BUTTON,
    CANCEL_BUTTON,
    MAIN_MENU_BUTTON,
)
from bot.dialogs.flows.settings.admin_settings.handlers import (
    add_admin_rights,
    del_admin_rights,
)
from bot.dialogs.flows.settings.admin_settings.states import AdminSettingsSG

logger = logging.getLogger(__name__)


admin_settings = Dialog(
    Window(
        Const(
            text='<b>===  Настройки Админов  ===</b>\n\n'
            '<code>Админ бота имеет все права Супер-Админа, '
            'кроме добавления/удаления Админов.</code>'
        ),
        Group(
            Row(
                SwitchTo(
                    text=Const('Добавить Админа'),
                    id='add_admin',
                    state=AdminSettingsSG.add_rights,
                    when=F['role'] == 'super_admin',
                ),
                SwitchTo(
                    text=Const('Удалить Админа'),
                    id='remove_admin',
                    state=AdminSettingsSG.remove_rights,
                    when=F['role'] == 'super_admin',
                ),
            ),
            SwitchTo(
                text=Const('Список Админов'),
                id='admin_list',
                state=AdminSettingsSG.list_admins,
                on_click=on_click_in_dev,
            ),
            CANCEL_BUTTON,
            MAIN_MENU_BUTTON,
        ),
        state=AdminSettingsSG.start,
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
        state=AdminSettingsSG.add_rights,
    ),
    Window(
        Format(
            'Подтвердите выдачу юзеру <b>{user_tg_id}</b> прав `Администратор`'
        ),
        Back(
            text=Const(text='✅ Подтвердить'),
            id='conf_rights',
            on_click=add_admin_rights,  # ty:ignore[invalid-argument-type]
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        state=AdminSettingsSG.confirm_rights,
    ),

    getter=[get_user_tg_id, get_access_flags],
)
