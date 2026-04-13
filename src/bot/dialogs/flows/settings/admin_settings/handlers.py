from aiogram.types import CallbackQuery, User as TelegramUser
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram_dialog import FromDishka, inject

from core.enum import Role
from db.repository.tg_user_repo import TGUserRepository


@inject
async def add_admin_rights(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    _tg_user_repo: FromDishka[TGUserRepository],
) -> None:
    user_tg_id = int(dialog_manager.dialog_data['user_tg_id'])
    existing_user = await _tg_user_repo.get_user_by_id(user_tg_id)

    if existing_user:
        if (
            existing_user.role == Role.ADMIN.value
            and existing_user.is_active
        ):
            await clbk.answer(
                '❌ Юзер уже имеет права `Админ`!', show_alert=True
            )
        else:
            await _tg_user_repo.update_user_role_and_status(
                telegram_id=user_tg_id, role=Role.ADMIN, is_active=True
            )
            await clbk.answer(
                f'✅ Юзеру {user_tg_id} успешно выданы права `Админ`!',
                show_alert=True,
            )
    else:
        telegram_user = TelegramUser(
            id=user_tg_id,
            is_bot=False,
            first_name='Unknown',
        )

        new_user = await _tg_user_repo.upsert_user(
            telegram_user=telegram_user, role=Role.ADMIN, is_active=True
        )

        if new_user:
            await clbk.answer(
                f'✅ Юзер {user_tg_id} добавлен в базу и выданы '
                f'права `Админ`!',
                show_alert=True,
            )
        else:
            await clbk.answer(
                '❌ Ошибка при добавлении юзера в базу!', show_alert=True
            )


@inject
async def del_admin_rights(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    _tg_user_repo: FromDishka[TGUserRepository],
) -> None:
    user_tg_id = int(dialog_manager.dialog_data['user_tg_id'])
    existing_user = await _tg_user_repo.get_user_by_id(user_tg_id)

    if existing_user and existing_user.role == Role.ADMIN.value:
        await _tg_user_repo.update_user_role_and_status(
            telegram_id=user_tg_id, role=Role.VISITOR, is_active=True
        )
        await clbk.answer(
            f'✅ Юзер {user_tg_id} успешно лишен прав `Админ`!',
            show_alert=True,
        )
    else:
        await clbk.answer(
            '❌ Юзер не имеет прав `Админ` или не найден в базе!',
            show_alert=True,
        )
