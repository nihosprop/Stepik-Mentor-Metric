import logging

from collections.abc import Sequence

from dishka.integrations.aiogram_dialog import FromDishka, inject

from db.models.telegram_user import User
from db.repository.tg_user_repo import TGUserRepository

logger = logging.getLogger(__name__)


@inject
async def get_visitors(
    tg_user_repo: FromDishka[TGUserRepository],
    **_kwargs,
) -> dict[str, Sequence[User] | int | str]:
    visitors = await tg_user_repo.get_all_visitors()

    return {
        'visitors': visitors,
        'count': len(visitors),
    }


@inject
async def get_list_visitors(
    tg_user_repo: FromDishka[TGUserRepository],
    **_kwargs,
) -> dict[str, list[str] | int]:
    visitors = [
        f'<a href="https://t.me/{item.username}">{item.full_name}</a>'
        f' ID: <code>{item.telegram_id}</code>'
        for item in await tg_user_repo.get_all_visitors()
        if item.username
    ]

    return {'visitors': visitors, 'count': len(visitors)}
