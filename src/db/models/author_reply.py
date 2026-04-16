from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base
from db.models.course import Course
from db.models.mixins import TimestampMixin
from db.models.stepik_user import StepikUser


class AuthorReply(TimestampMixin, Base):
    __tablename__ = 'author_replies'

    comment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey('courses.course_id'), index=True, nullable=False
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey('stepik_users.user_id'), index=True, nullable=False
    )
    parent_comment_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    is_mentor_reply: Mapped[bool] = mapped_column(
        default=True, server_default='true', nullable=False
    )
    is_useful_comment: Mapped[bool] = mapped_column(
        default=False, server_default='false', nullable=False
    )
    comment_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    author: Mapped[StepikUser] = relationship(back_populates='replies')
    course: Mapped[Course] = relationship(back_populates='replies')
