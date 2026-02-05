import logging

from dataclasses import dataclass

from aiogram.types import User as TelegramUser
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User

logger = logging.getLogger(__name__)


@dataclass
class UserRepository:
    session: AsyncSession

    async def _user_exists(self, telegram_id: int) -> bool | None:
        stmt = select(exists().where(User.telegram_id == telegram_id))
        return await self.session.scalar(stmt)

    async def add_if_not_exists(self, telegram_user: TelegramUser) -> None:
        """
        Add a user if it doesn't exist
        Args:
            telegram_user: Telegram user object
        Returns:
            None
        """
        telegram_id: int = telegram_user.id

        if await self._user_exists(telegram_id):
            logger.debug(f'User {telegram_id} already exists')
            return

        user = User(
            telegram_id=telegram_id,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            username=telegram_user.username,
        )
        self.session.add(user)

        logger.info(
            f'Created new user {telegram_id}:{telegram_user.first_name}'
        )
