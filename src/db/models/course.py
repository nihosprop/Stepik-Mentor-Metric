from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base
from db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from .author_reply import AuthorReply
    from .mentor_statistic import MentorStatistic


class Course(TimestampMixin, Base):
    __tablename__ = 'courses'

    course_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    replies: Mapped[list[AuthorReply]] = relationship(back_populates='course')
    statistics: Mapped[list[MentorStatistic]] = relationship(
        back_populates='course'
    )
