from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka, inject

from core.main_config import Config


@inject
async def get_pars_mode(
    dialog_manager: DialogManager,
    event_from_user: User,
    config: FromDishka[Config],
        **_kwargs
) -> dict[str, Any]:
    name = event_from_user.first_name
    pars_mode = config.bot.parse_mode
    return {'user_name': name, 'pars_mode': pars_mode}
