from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base
from db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from .course import Course
    from .stepik_user import StepikUser


class MentorStatistic(TimestampMixin, Base):
    __tablename__ = 'statistics'

    id: Mapped[int] = mapped_column(primary_key=True)
    mentor_id: Mapped[int] = mapped_column(
        ForeignKey('stepik_users.user_id'), index=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.course_id'), index=True
    )
    stat_date: Mapped[date] = mapped_column(Date, index=True)

    total_comments: Mapped[int] = mapped_column(Integer, default=0)
    replies_count: Mapped[int] = mapped_column(Integer, default=0)
    helpful_replies_count: Mapped[int] = mapped_column(Integer, default=0)

    avg_response_time_seconds: Mapped[float] = mapped_column(nullable=True)
    help_index: Mapped[float] = mapped_column(Float, default=0.0)

    mentor: Mapped[StepikUser] = relationship(back_populates='statistics')
    course: Mapped[Course] = relationship(back_populates='statistics')

    __table_args__ = (
        Index(
            'ix_stat_date_mentor_course',
            'stat_date',
            'mentor_id',
            'course_id',
            unique=True,
        ),
    )
