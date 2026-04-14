import logging

from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Group,
    NextPage,
    PrevPage,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, List

from bot.dialogs.common.getters import get_user_tg_id
from bot.dialogs.common.handlers import (
    correct_tg_user_id,
    error_tg_user_id,
    no_text,
)
from bot.dialogs.common.validators import check_tg_user_id
from bot.dialogs.common.widgets import (
    BACK_BUTTON,
    CANCEL_BUTTON,
    MAIN_MENU_BUTTON,
)
from bot.dialogs.flows.settings.visitor_settings.getters import (
    get_list_visitors,
    get_visitors,
)
from bot.dialogs.flows.settings.visitor_settings.handlers import (
    add_visitor_rights,
    del_visitor_rights,
    on_visitor_selected,
)
from bot.dialogs.flows.settings.visitor_settings.states import (
    VisitorSettingsSG,
)

logger = logging.getLogger(__name__)

visitor_settings = Dialog(
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
                ),
            ),
            SwitchTo(
                text=Const('Список визитёров'),
                id='mentors_list',
                state=VisitorSettingsSG.list_visitors,
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
    Window(
        Format(
            'Найдено Визитёров: {count}\nВыберите нужного для удаления:',
            when=F['count'] > 0,
        ),
        Const(text='Визитёров для удаления не найдено!', when=F['count'] == 0),
        ScrollingGroup(
            Select(
                Format(text='{item.full_name}'),
                id='s_visitor',
                item_id_getter=lambda x: x.telegram_id,
                items='visitors',
                on_click=on_visitor_selected,
            ),
            id='visitors_scroll',
            width=1,
            height=4,
            hide_pager=True,
        ),
        Row(
            PrevPage(
                scroll='visitors_scroll',
                text=Format(text='{data[prev_page_button]}'),
            ),
            NextPage(
                scroll='visitors_scroll',
                text=Format(text='{data[next_page_button]}'),
            ),
            when=F['count'] > 4,
        ),
        MAIN_MENU_BUTTON,
        SwitchTo(
            Const('◀️ Назад'), id='in_start_1', state=VisitorSettingsSG.start
        ),
        state=VisitorSettingsSG.remove_rights,
        getter=get_visitors,
    ),
    Window(
        Format(text='Подтвердите удаление прав Визитёра!'),
        SwitchTo(
            text=Const(text='✅ Подтвердить'),
            id='conf_del_visitor',
            on_click=del_visitor_rights,  # ty:ignore[invalid-argument-type]
            state=VisitorSettingsSG.remove_rights,
        ),
        MAIN_MENU_BUTTON,
        BACK_BUTTON,
        state=VisitorSettingsSG.confirm_remove_rights,
    ),
    Window(
        Const(text='👥 <b>Список Визитёров:</b>', when=F['count'] > 0),
        Const(text='<b>Визитёров не обнаружено.</b>', when=F['count'] <= 0),
        List(
            Format(text='{item}'),
            items='visitors',
        ),
        MAIN_MENU_BUTTON,
        SwitchTo(
            Const('◀️ Назад'), id='in_start_2', state=VisitorSettingsSG.start
        ),
        getter=get_list_visitors,
        state=VisitorSettingsSG.list_visitors,
        disable_web_page_preview=True,
    ),
    getter=get_user_tg_id,
)
