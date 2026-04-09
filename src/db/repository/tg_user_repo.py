import logging

from dataclasses import dataclass

from aiogram.types import User as TelegramUser
from sqlalchemy import delete, exists, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.enum import Role
from db.models.telegram_user import User

logger = logging.getLogger(__name__)


@dataclass
class TGUserRepository:
    """
    Telegram User Repository
    """

    session: AsyncSession

    async def _user_exists(self, telegram_id: int) -> bool | None:
        stmt = select(exists().where(User.telegram_id == telegram_id))
        return await self.session.scalar(stmt)

    async def upsert_user(
        self, telegram_user: TelegramUser, role: Role, is_active: bool
    ) -> User | None:
        first_name = telegram_user.first_name or 'Unknown'

        insert_stmt = insert(User).values(
            telegram_id=telegram_user.id,
            first_name=first_name,
            last_name=telegram_user.last_name,
            username=telegram_user.username,
            role=role,
            is_active=is_active,
        )
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['telegram_id'],
            set_={
                'first_name': first_name,
                'last_name': telegram_user.last_name,
                'username': telegram_user.username,
            },
        )
        await self.session.execute(upsert_stmt)
        logger.debug(f'Upserted user {telegram_user.id}')
        return await self.get_user_by_id(telegram_user.id)

    async def get_user(self, telegram_user: TelegramUser) -> User | None:
        if await self._user_exists(telegram_user.id):
            stmt = select(User).where(User.telegram_id == telegram_user.id)
            return await self.session.scalar(stmt)
        return None

    async def update_user_profile(self, telegram_user: TelegramUser) -> None:
        """Updates only the username, without affecting the role and status."""
        first_name = telegram_user.first_name or 'Unknown'
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_user.id)
            .values(
                first_name=first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
            )
        )
        await self.session.execute(stmt)

    async def get_user_by_id(self, telegram_id: int) -> User | None:
        """Gets a user by ID in one request."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        return await self.session.scalar(stmt)

    async def delete_user(self, telegram_user: TelegramUser) -> None:
        stmt = delete(User).where(User.telegram_id == telegram_user.id)
        await self.session.execute(stmt)
