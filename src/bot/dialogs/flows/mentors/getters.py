import logging

from collections.abc import Sequence
from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import FromDishka, inject

from db.models import StepikUser
from db.repository.stepik_user_repo import StepikUserRepo

logger = logging.getLogger(__name__)


async def get_stepik_username(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    return {
        'stepik_username': dialog_manager.dialog_data.get('stepik_username')
    }


@inject
async def get_mentors(
    dialog_manager: DialogManager,
    stepik_user_repo: FromDishka[StepikUserRepo],
    **_kwargs,
) -> dict[str, Sequence[StepikUser] | int | str]:
    mentors = await stepik_user_repo.get_all_mentors()
    count_mentors = len(mentors)
    scroll = dialog_manager.find('mentors_scroll')

    current_page = await scroll.get_page() if scroll else 0
    last_page_index = max(0, (count_mentors - 1) // 4)

    is_first = current_page == 0
    is_last = current_page >= last_page_index

    prev_button_text = ' ' if is_first else '◀️'
    next_button_text = ' ' if is_last else '▶️'

    return {
        'mentors': mentors,
        'count': count_mentors,
        'prev_page_button': prev_button_text,
        'next_page_button': next_button_text,
    }


@inject
async def get_list_mentors(
    stepik_user_repo: FromDishka[StepikUserRepo],
    **_kwargs,
) -> dict[str, list[str] | int]:
    mentors = [
        f'\n<a href="https://stepik.org/users/'
        f'{item.user_id}/profile">{i}. {item.full_name}</a>'
        f'\nID: <code>{item.user_id}</code>'
        for i, item in enumerate(
            await stepik_user_repo.get_all_mentors(), start=1
        )
    ]

    return {'mentors': mentors, 'count': len(mentors)}
