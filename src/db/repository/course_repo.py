import logging

from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import delete, exists, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Course

logger = logging.getLogger(__name__)


@dataclass
class CourseRepo:
    session: AsyncSession

    async def _course_exists(self, course_id: int) -> bool | None:
        stmt = select(exists().where(Course.course_id == course_id))
        return await self.session.scalar(stmt)

    async def delete_course(self, course_id: int) -> None:
        stmt = delete(Course).where(Course.course_id == course_id)
        await self.session.execute(stmt)
        logger.debug(f'Deleted Stepik course ID: {course_id}')

    async def upsert_course(
        self, course_id: int, title: str, is_active: bool = True
    ) -> None:
        insert_stmt = insert(Course).values(
            course_id=course_id, title=title, is_active=is_active
        )
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['course_id'],
            set_={
                'title': title,
                'is_active': is_active,
            },
        )
        await self.session.execute(upsert_stmt)
        logger.debug(f'Upserted Stepik course {course_id}')

    async def get_stepik_course(self, course_id: int) -> Course | None:
        """Gets a course object by ID."""
        stmt = select(Course).where(Course.course_id == course_id)
        return await self.session.scalar(stmt)

    async def get_all_courses(self) -> Sequence[Course]:
        """Returns a list of all courses who have is_active=True"""
        stmt = select(Course).where(Course.is_active)
        result = await self.session.execute(stmt)
        return result.scalars().all()
