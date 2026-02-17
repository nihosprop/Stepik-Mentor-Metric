from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
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
    period_start: Mapped[datetime] = mapped_column(DateTime)
    replies_count: Mapped[int] = mapped_column(default=0)
    avg_response_time_seconds: Mapped[float] = mapped_column(nullable=True)

    mentor: Mapped[StepikUser] = relationship(back_populates='replies')
    course: Mapped[Course] = relationship(back_populates='replies')
