from aiogram.types import CallbackQuery, ChatFullInfo, Message


def get_username(
        _type_update: Message | CallbackQuery | ChatFullInfo,
        default: str = 'Anonymous',
        ) -> str:
    result = default

    if isinstance(_type_update, ChatFullInfo):
        if _type_update.type == 'private':
            if _type_update.username and _type_update.username.strip():
                result = f'@{_type_update.username.strip()}'
            elif _type_update.first_name and _type_update.first_name.strip():
                result = _type_update.first_name.strip()
        elif _type_update.title and _type_update.title.strip():
            result = _type_update.title.strip()
    else:
        user = getattr(_type_update, 'from_user', None)
        if user:
            if user.username and user.username.strip():
                result = f'@{user.username.strip()}'
            elif user.first_name and user.first_name.strip():
                result = user.first_name.strip()

    return result
