import logging

from aiogram.types import CallbackQuery, Message, User as TelegramUser
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram_dialog import FromDishka, inject

from core.enum import Role
from db.repository.tg_user_repo import TGUserRepository

logger = logging.getLogger(__name__)


async def correct_tg_user_id(
    _msg: Message,
    _widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    logger.debug('Entry')

    dialog_manager.dialog_data['user_tg_id'] = text
    await dialog_manager.next()

    logger.debug('Exit')


async def error_tg_user_id(
    msg: Message,
    _widget: ManagedTextInput,
    _dialog_manager: DialogManager,
    _error: ValueError,
) -> None:
    logger.debug('Entry')

    await msg.delete()
    await msg.answer(
        text='Вы ввели некорректный ID юзера! Попробуйте еще раз.'
    )

    logger.debug('Exit')


async def no_text(
    msg: Message, _widget: MessageInput, _dialog_manager: DialogManager
) -> None:
    await msg.answer(text='Вы ввели не текст!', show_alert=True)


@inject
async def add_visitor_rights(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    _tg_user_repo: FromDishka[TGUserRepository],
) -> None:
    logger.debug('Entry')

    user_tg_id = int(dialog_manager.dialog_data['user_tg_id'])
    existing_user = await _tg_user_repo.get_user_by_id(user_tg_id)

    if existing_user:
        if (
            existing_user.role == Role.VISITOR.value
            and existing_user.is_active
        ):
            await clbk.answer(
                '❌ Юзер уже имеет права `Визитёр`!', show_alert=True
            )
        else:
            await _tg_user_repo.update_user_role_and_status(
                telegram_id=user_tg_id, role=Role.VISITOR, is_active=True
            )
            await clbk.answer(
                f'✅ Юзеру {user_tg_id} успешно выданы права `Визитёр`!',
                show_alert=True,
            )
    else:
        telegram_user = TelegramUser(
            id=user_tg_id,
            is_bot=False,
            first_name='Unknown',
        )

        new_user = await _tg_user_repo.upsert_user(
            telegram_user=telegram_user, role=Role.VISITOR, is_active=True
        )

        if new_user:
            await clbk.answer(
                f'✅ Юзер {user_tg_id} добавлен в базу и выданы '
                f'права `Визитёр`!',
                show_alert=True,
            )
        else:
            await clbk.answer(
                '❌ Ошибка при добавлении юзера в базу!', show_alert=True
            )

    logger.debug('Exit')
