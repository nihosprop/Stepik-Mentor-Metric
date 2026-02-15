import logging

from dataclasses import dataclass

from aiogram.types import User as TelegramUser
from sqlalchemy import delete, exists, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.telegram_user import User

logger = logging.getLogger(__name__)


@dataclass
class TGUserRepository:
    """
    User Repository
    """
    session: AsyncSession

    async def _user_exists(self, telegram_id: int) -> bool | None:
        stmt = select(exists().where(User.telegram_id == telegram_id))
        return await self.session.scalar(stmt)

    async def upsert_user(self, telegram_user: TelegramUser) -> None:
        insert_stmt = insert(User).values(
            telegram_id=telegram_user.id,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            username=telegram_user.username,
        )
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['telegram_id'],
            set_={
                'first_name': telegram_user.first_name,
                'last_name': telegram_user.last_name,
                'username': telegram_user.username,
            },
        )
        await self.session.execute(upsert_stmt)
        logger.debug(f'Upserted user {telegram_user.id}')

    async def get_user(self, telegram_user: TelegramUser) -> User | None:
        if await self._user_exists(telegram_user.id):
            stmt = select(User).where(User.telegram_id == telegram_user.id)
            return await self.session.scalar(stmt)
        return None

    async def delete_user(self, telegram_user: TelegramUser) -> None:
        stmt = delete(User).where(User.telegram_id == telegram_user.id)
        await self.session.execute(stmt)