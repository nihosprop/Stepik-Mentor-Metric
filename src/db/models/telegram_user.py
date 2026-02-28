from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base
from db.models.mixins import TimestampMixin


# TODO: add fields `is_admin`, `is_mentor`
class User(TimestampMixin, Base):
    __tablename__ = 'tg_users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
