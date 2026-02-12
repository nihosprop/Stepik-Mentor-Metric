from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base
from db.models.mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, primary_key=True
    )
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)