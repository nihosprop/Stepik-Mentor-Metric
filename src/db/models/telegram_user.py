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
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='visitor',
        server_default='visitor',
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default='false'
    )

    @property
    def full_name(self) -> str:
        """Returns the full name of the user."""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.first_name or 'Unknown'
