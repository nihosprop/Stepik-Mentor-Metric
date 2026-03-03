from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base
from db.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from .author_reply import AuthorReply
    from .mentor_statistic import MentorStatistic


class StepikUser(TimestampMixin, Base):
    __tablename__ = 'stepik_users'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_mentor: Mapped[bool] = mapped_column(default=False)

    replies: Mapped[list[AuthorReply]] = relationship(back_populates='author')
    statistics: Mapped[list[MentorStatistic]] = relationship(
        back_populates='mentor'
    )
