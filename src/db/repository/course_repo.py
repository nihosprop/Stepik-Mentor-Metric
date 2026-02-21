import logging

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@dataclass
class CourseRepo:
    session: AsyncSession

    async def add_course(self, course_id: int, course_title: str) -> None:
        logger.debug(f'Adding course {course_title}')

    async def delete_course(self, course_id: int) -> None:
        logger.debug(f'Deleting course {course_id}')
