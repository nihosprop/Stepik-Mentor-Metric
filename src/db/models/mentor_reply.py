from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models import Base, Course, TimestampMixin
from db.models.stepik_user import StepikUser


class MentorReply(TimestampMixin, Base):
    __tablename__ = 'mentor_replies'

    comment_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, primary_key=True
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.course_id'), index=True, nullable=False
    )
    mentor_id: Mapped[int] = mapped_column(
        ForeignKey('stepik_users.user_id'), index=True, nullable=False
    )
    parent_comment_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    stepik_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    mentor: Mapped[StepikUser] = relationship(back_populates='replies')
    course: Mapped[Course] = relationship(back_populates='replies')
