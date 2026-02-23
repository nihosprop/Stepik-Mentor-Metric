import logging

from collections.abc import Sequence
from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import FromDishka, inject

from db.models import Course
from db.repository.course_repo import CourseRepo

logger = logging.getLogger(__name__)


@inject
async def get_course_title(
    dialog_manager: DialogManager, event_from_user: User, **_kwargs
) -> dict[str, Any]:
    return {'course_title': dialog_manager.dialog_data.get('course_title')}


@inject
async def get_courses(
    dialog_manager: DialogManager,
    event_from_user: User,
    course_repo: FromDishka[CourseRepo],
    **_kwargs,
) -> dict[str, Sequence[Course] | int]:
    courses = await course_repo.get_all_courses()
    return {'mentors': courses, 'count': len(courses)}


@inject
async def get_list_courses(
    dialog_manager: DialogManager,
    event_from_user: User,
    course_repo: FromDishka[CourseRepo],
    **_kwargs,
) -> dict[str, list[str] | int]:
    mentors = [
        f'<a href="https://stepik.org/course/'
        f'{item.course_id}/info">{item.title}</a>'
        f' ID: <code>{item.course_id}</code>'
        for item in await course_repo.get_all_courses()
    ]
    return {'mentors': mentors, 'count': len(mentors)}
