import logging

from dataclasses import dataclass

from aiogram.types import User as TelegramUser
from sqlalchemy import delete, exists, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Course
from db.models.telegram_user import User

logger = logging.getLogger(__name__)

@dataclass
class CourseRepo:
    session: AsyncSession

    async def add_course(self, course: Course) -> Course:
        pass

    async def delete_course(self, course_id: int) -> None:
        pass

