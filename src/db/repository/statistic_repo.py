import calendar

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time

from sqlalchemy import asc, case, cast, desc, func, not_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.sqltypes import Text

from db.models import AuthorReply, Course, MentorStatistic, StepikUser


@dataclass
class StatisticRepo:
    session: AsyncSession

    async def get_monthly_stats(self, year: int, month: int) -> Sequence:
        """
        Aggregates data from the statistics table for a specified month.
        """
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        kpd_expr = case(
            (
                func.sum(MentorStatistic.helpful_replies_count) > 0,
                func.sum(MentorStatistic.helpful_replies_count)
                * func.sum(MentorStatistic.helpful_replies_count)
                / func.sum(MentorStatistic.total_comments),
            ),
            else_=(
                func.sum(MentorStatistic.replies_count)
                * func.sum(MentorStatistic.replies_count)
                / func.sum(MentorStatistic.total_comments)
            ),
        )

        stmt = (
            select(
                StepikUser.full_name,
                Course.title.label('course_title'),
                func.sum(MentorStatistic.total_comments).label('total_t'),
                func.sum(MentorStatistic.replies_count).label('total_h'),
                func.sum(MentorStatistic.helpful_replies_count).label(
                    'total_helpful'
                ),
                func.avg(MentorStatistic.avg_response_time_seconds).label(
                    'avg_delay'
                ),
            )
            .join(StepikUser, StepikUser.user_id == MentorStatistic.mentor_id)
            .join(Course, Course.course_id == MentorStatistic.course_id)
            .where(
                MentorStatistic.stat_date.between(start_date, end_date),
            )
            .group_by(StepikUser.full_name, Course.title)
        ).order_by(
            Course.title,
            desc(kpd_expr),
            desc('total_h'),
            asc('avg_delay').nulls_last(),
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return rows

    async def get_general_stats(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> Sequence:
        """
        Gets aggregated statistics for all mentors across all courses
         for specified period.

        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)

        Returns:
            Sequence: Aggregated statistics for each mentor across all courses.
        """

        kpd_expr = case(
            (
                func.sum(MentorStatistic.helpful_replies_count) > 0,
                func.sum(MentorStatistic.helpful_replies_count)
                * func.sum(MentorStatistic.helpful_replies_count)
                / func.sum(MentorStatistic.total_comments),
            ),
            else_=(
                func.sum(MentorStatistic.replies_count)
                * func.sum(MentorStatistic.replies_count)
                / func.sum(MentorStatistic.total_comments)
            ),
        )

        stmt = select(
            StepikUser.full_name,
            func.sum(MentorStatistic.total_comments).label('total_t'),
            func.sum(MentorStatistic.replies_count).label('total_h'),
            func.sum(MentorStatistic.helpful_replies_count).label(
                'total_helpful'
            ),
            func.avg(MentorStatistic.avg_response_time_seconds).label(
                'avg_delay'
            ),
            cast(None, Text).label('course_title'),
        ).join(StepikUser, StepikUser.user_id == MentorStatistic.mentor_id)

        # Добавляем фильтрацию по периоду, если указаны даты
        if start_date and end_date:
            stmt = stmt.where(
                MentorStatistic.stat_date.between(start_date, end_date)
            )
        elif start_date:
            stmt = stmt.where(MentorStatistic.stat_date >= start_date)
        elif end_date:
            stmt = stmt.where(MentorStatistic.stat_date <= end_date)

        stmt = stmt.group_by(StepikUser.full_name).order_by(
            desc(kpd_expr),
            desc('total_h'),
            asc('avg_delay').nulls_last(),
        )

        result = await self.session.execute(stmt)
        return result.all()

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

    async def get_report_from_stats(self, target_date: date) -> Sequence:
        """
        Gets ready-made statistics for a specific day from
         the table MentorStatistic. Already here help_index и avg_delay.
        """
        stmt = (
            select(
                StepikUser.full_name,
                Course.title.label('course_title'),
                MentorStatistic.total_comments,
                MentorStatistic.replies_count,
                MentorStatistic.help_index,
                MentorStatistic.avg_response_time_seconds.label('avg_delay'),
            )
            .join(StepikUser, StepikUser.user_id == MentorStatistic.mentor_id)
            .join(Course, Course.course_id == MentorStatistic.course_id)
            .where(MentorStatistic.stat_date == target_date)
            .order_by(
                Course.title,
                desc(MentorStatistic.help_index),
                asc(MentorStatistic.avg_response_time_seconds).nulls_last(),
            )
        )

        result = await self.session.execute(stmt)
        return result.all()

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
                AuthorReply.is_mentor_reply,
                AuthorReply.parent_comment_id.is_not(None),
                AuthorReply.comment_created_at.between(start_date, end_date),
                not_(
                    AuthorReply.parent_comment_id.in_(
                        select(AuthorReply.comment_id).where(
                            AuthorReply.is_mentor_reply
                        )
                    )
                ),
            )
            .group_by(Course.title, StepikUser.full_name)
            .order_by(Course.title, desc('replies_count'))
        )
        result = await self.session.execute(stmt)
        return result.all()

    # TODO: take to another place
    async def calculate_and_save_daily_stats(self, target_date: date) -> None:
        """Calculates the daily statistics for a specified period.
        Args:
            target_date (date): The target date.
        Returns:
            None
        """
        start_date = datetime.combine(target_date, time.min, tzinfo=UTC)

        if target_date == datetime.now(UTC).date():
            end_date = datetime.now(UTC)
        else:
            end_date = datetime.combine(target_date, time.max, tzinfo=UTC)

        active_mentors_stmt = (
            select(AuthorReply.author_id, AuthorReply.course_id)
            .join(StepikUser, AuthorReply.author_id == StepikUser.user_id)
            .where(
                StepikUser.is_mentor.is_(True),
                AuthorReply.comment_created_at >= start_date,
                AuthorReply.comment_created_at <= end_date,
            )
            .distinct()
        )
        active_mentors: Sequence = (
            await self.session.execute(active_mentors_stmt)
        ).all()

        for mentor_id, course_id in active_mentors:
            replies_stmt = select(AuthorReply).where(
                AuthorReply.author_id == mentor_id,
                AuthorReply.course_id == course_id,
                AuthorReply.comment_created_at >= start_date,
                AuthorReply.comment_created_at <= end_date,
            )
            mentor_replies = (
                (await self.session.execute(replies_stmt)).scalars().all()
            )

            total_comments = len(mentor_replies)
            replies_count = 0
            helpful_replies_count = 0
            total_delay = 0.0
            timed_replies = 0

            for reply in mentor_replies:
                if reply.parent_comment_id is not None:
                    replies_count += 1

                    parent_stmt = select(AuthorReply).where(
                        AuthorReply.comment_id == reply.parent_comment_id
                    )
                    parent_comment = (
                        await self.session.execute(parent_stmt)
                    ).scalar_one_or_none()

                    if parent_comment:
                        # Считаем полезным ответ только на осмысленный вопрос
                        if parent_comment.is_useful_comment:
                            helpful_replies_count += 1

                        delay = (
                            reply.comment_created_at
                            - parent_comment.comment_created_at
                        ).total_seconds()
                        total_delay += delay
                        timed_replies += 1

            avg_delay = (
                (total_delay / timed_replies) if timed_replies > 0 else None
            )
            # h_idx: helpful_replies_count^2 / total_comments
            perf_index = (
                (helpful_replies_count**2 / total_comments)
                if total_comments > 0
                else 0
            )

            stmt = (
                insert(MentorStatistic)
                .values(
                    mentor_id=mentor_id,
                    course_id=course_id,
                    stat_date=target_date,
                    total_comments=total_comments,
                    replies_count=replies_count,
                    helpful_replies_count=helpful_replies_count,
                    help_index=perf_index,
                    avg_response_time_seconds=avg_delay,
                )
                .on_conflict_do_update(
                    index_elements=['stat_date', 'mentor_id', 'course_id'],
                    set_={
                        'total_comments': total_comments,
                        'replies_count': replies_count,
                        'helpful_replies_count': helpful_replies_count,
                        'help_index': perf_index,
                        'avg_response_time_seconds': avg_delay,
                        'created_at': func.now(),
                    },
                )
            )
            await self.session.execute(stmt)
