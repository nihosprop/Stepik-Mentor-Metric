from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base
from db.models.mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = 'tg_users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_admin: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default='false'
    )
    is_visitor: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default='false'
    )
