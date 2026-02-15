from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models import Base, TimestampMixin
from db.models.mentor_reply import MentorReply


class StepikUser(TimestampMixin, Base):
    __tablename__ = 'stepik_users'

    user_id: Mapped[int] = mapped_column(
        BigInteger, index=True, primary_key=True
    )
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_mentor: Mapped[bool] = mapped_column(default=False)

    replies: Mapped[list[MentorReply]] = relationship(back_populates='mentor')
