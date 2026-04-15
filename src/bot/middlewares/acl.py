import logging

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from aiogram_dialog.api.exceptions import UnknownState
from dishka import AsyncContainer

from core.enum import Role
from core.main_config import Config
from db.repository.tg_user_repo import TGUserRepository

logger = logging.getLogger(__name__)


class ACLMiddleware(BaseMiddleware):
    """
    Middleware to check access rights to the bot.

    This middleware checks the user's access rights to the bot.
    If the user is a super admin, he is granted access. Otherwise,
    the middleware checks the user's role and active status in the
    database. If the user is inactive or his role is not defined,
    the middleware denies access. If the user's profile information
    differs from the stored information, the middleware updates the
    user's profile in the database.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]] | None:
        """
        Args:
            handler(
                Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]):
                   The handler function to which the middleware is applied.
            event(TelegramObject): The event object.
            data(dict[str, Any]): The data dictionary.
        Returns:
            Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]] | None:
                The handler function or None if the user access is denied.
        """
        logger.debug(f'Entry {self.__class__.__name__}')

        try:
            user: User | None = data.get('event_from_user')
            logger.debug(
                f'{type(event).__name__}, user_id={user.id if user else None}'
            )
            if not user or not isinstance(user, User):
                logger.debug('User not found or not instance of User')
                return await handler(event, data)

            container: AsyncContainer = data['dishka_container']
            config: Config = await container.get(Config)
            tg_user_repo: TGUserRepository = await container.get(
                TGUserRepository
            )

            if user.id in config.bot.admins:
                data['role'] = Role.SUPER_ADMIN.value
                logger.debug(f'Super-admin {user.id} granted access')
                return await handler(event, data)

            user_from_db = await tg_user_repo.get_user(user)
            if not user_from_db or not user_from_db.is_active:
                logger.info(f'User {user.id} access denied')
                return None

            data['role'] = user_from_db.role
            logger.debug(f'User {user.id} role={user_from_db.role}')

            if (
                user_from_db.first_name != user.first_name
                or user_from_db.username != user.username
            ):
                await tg_user_repo.update_user_profile(
                    telegram_user=user,
                )
            logger.debug(f'{user_from_db.is_active=}')
            logger.debug(f'Exit {self.__class__.__name__}')
            return await handler(event, data)
        except UnknownState as e:
            logger.warning(f'ACLMiddleware caught exception: {e} and raised')
            raise
        except Exception as e:
            logger.error(f'ACLMiddleware caught exception: {e}', exc_info=True)
            return await handler(event, data)
