import logging

from dataclasses import dataclass

from aiogram.types import User as TelegramUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User

logger = logging.getLogger(__name__)


@dataclass
class UserRepository:
    session: AsyncSession

    async def add_if_not_exists(self, telegram_user: TelegramUser) -> None:
        telegram_id: int = telegram_user.id

        stmt = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )

        existing_user: User | None = stmt.scalar_one_or_none()

        if not existing_user:
            new_user = User(
                telegram_id=telegram_id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
            )
            self.session.add(new_user)
            await self.session.commit()
            logger.info(f'User {telegram_id}:{new_user.username} created')
            return

        logger.info(f'User {telegram_id} already exists')
