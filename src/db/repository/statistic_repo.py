from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, time

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import AuthorReply, Course, StepikUser


@dataclass
class StatisticRepo:
    session: AsyncSession

    async def get_current_day_stats(self) -> Sequence:
        """
        Gets statistics for the current day.

        Returns:
            Sequence: A sequence of tuples containing the full name
             of the mentor,the title of the course, and the number of
             replies made by the mentor in the course during the current day.
        """
        now = datetime.now(UTC)
        start_of_day = datetime.combine(now.date(), time.min, tzinfo=UTC)

        return await self.get_stats_for_period(start_of_day, now)

    async def get_stats_for_period(
        self, start_date: datetime, end_date: datetime
    ) -> Sequence:
        """Gets statistics for a specified period.

        Args:
            start_date (datetime): The start of the period.
            end_date (datetime): The end of the period.

        Returns:
            Sequence: A sequence of tuples containing the full name
             of the mentor,the title of the course, and the number of
             replies made by the mentor in the course during the period.
        """

        stmt = (
            select(
                StepikUser.full_name,
                Course.title.label('course_title'),
                func.count(AuthorReply.comment_id).label('replies_count'),
            )
            .join(AuthorReply, StepikUser.user_id == AuthorReply.author_id)
            .join(Course, Course.course_id == AuthorReply.course_id)
            .where(
                and_(
                    AuthorReply.is_mentor_reply,
                    AuthorReply.comment_created_at >= start_date,
                    AuthorReply.comment_created_at <= end_date,
                )
            )
            .group_by(Course.title, StepikUser.full_name)
            .order_by(Course.title, desc('replies_count'))
        )
        result = await self.session.execute(stmt)
        return result.all()
