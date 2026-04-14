import logging

from collections.abc import Sequence
from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import FromDishka, inject

from db.models import Course
from db.repository.course_repo import CourseRepo

logger = logging.getLogger(__name__)


async def get_course_title(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    return {'course_title': dialog_manager.dialog_data.get('course_title')}


@inject
async def get_courses(
    dialog_manager: DialogManager,
    course_repo: FromDishka[CourseRepo],
    **_kwargs,
) -> dict[str, Sequence[Course] | int | str]:
    courses = await course_repo.get_all_courses()
    count_courses = len(courses)
    scroll = dialog_manager.find('courses_scroll')
    current_page = await scroll.get_page() if scroll else 0
    last_page_index = max(0, (count_courses - 1) // 4)

    is_first = current_page == 0
    is_last = current_page >= last_page_index

    prev_button_text = ' ' if is_first else '◀️'
    next_button_text = ' ' if is_last else '▶️'

    return {
        'courses': courses,
        'count': count_courses,
        'prev_page_button': prev_button_text,
        'next_page_button': next_button_text,
    }


@inject
async def get_list_courses(
    course_repo: FromDishka[CourseRepo],
    **_kwargs,
) -> dict[str, list[str] | int]:
    courses = [
        f'\n<a href="https://stepik.org/course/'
        f'{item.course_id}/info">{item.title}</a>\n'
        f'ID: <code>{item.course_id}</code>'
        for item in await course_repo.get_all_courses()
    ]
    return {'courses': courses, 'count': len(courses)}
