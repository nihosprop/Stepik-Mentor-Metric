from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models import Base, TimestampMixin
from db.models.course import Course
from db.models.stepik_user import StepikUser


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
