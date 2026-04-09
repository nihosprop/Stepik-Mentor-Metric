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
    Repository for working with Telegram users in the database.
    Attributes:
        session (AsyncSession): The session to use for database operations.
    """

    session: AsyncSession

    async def _user_exists(self, telegram_id: int) -> bool | None:
        """
        Checks if a user with the given Telegram ID exists in the database.

        Args:
            telegram_id (int): The ID of the user to check.
        Returns:
            bool | None:
             True if the user exists,
              False if they do not, or None if an error occurred.
        """
        stmt = select(exists().where(User.telegram_id == telegram_id))
        return await self.session.scalar(stmt)

    async def upsert_user(
        self, telegram_user: TelegramUser, role: Role, is_active: bool
    ) -> User | None:
        """
        Inserts a new user or updates an existing one in the database.

        Args:
            telegram_user (TelegramUser): The user's Telegram information.
            role (Role): The user's role.
            is_active (bool): Whether the user is active or not.
        Returns:
            User | None:
             The updated or inserted user object, or None if an error occurred.
        """
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
        """
        Gets a user from the database by their Telegram ID.

        Args:
            telegram_user (TelegramUser): The user's Telegram information.

        Returns:
            User | None: The user object if it exists, or None if it does not.
        """
        if await self._user_exists(telegram_user.id):
            stmt = select(User).where(User.telegram_id == telegram_user.id)
            return await self.session.scalar(stmt)
        return None

    async def update_user_profile(self, telegram_user: TelegramUser) -> None:
        """
        Updates a user's profile information in the database.

        Args:
            telegram_user (TelegramUser): The user's Telegram information.
        """
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

    async def update_user_role_and_status(
        self, telegram_id: int, role: Role, is_active: bool
    ) -> None:
        """
        Updates a user's role and active status in the database.

        Args:
            telegram_id (int): The Telegram ID of the user to update.
            role (Role): The new role for the user.
            is_active (bool): The new active status for the user.
        """
        stmt = (
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(role=role.value, is_active=is_active)
        )
        await self.session.execute(stmt)

    async def get_user_by_id(self, telegram_id: int) -> User | None:
        """
        Gets a user from the database by their Telegram ID.

        Args:
            telegram_id (int): The ID of the user to get.

        Returns:
            User | None: The user object if it exists, or None if it does not.
        """
        stmt = select(User).where(User.telegram_id == telegram_id)
        return await self.session.scalar(stmt)

    async def delete_user(self, telegram_user: TelegramUser) -> None:
        """
        Deletes a user from the database by their Telegram ID.

        Args:
            telegram_user (TelegramUser): The user's Telegram information.
        """
        stmt = delete(User).where(User.telegram_id == telegram_user.id)
        await self.session.execute(stmt)
