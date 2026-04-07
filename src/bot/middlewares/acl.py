import logging

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, User
from dishka import AsyncContainer

from core.enum import Role
from core.main_config import Config
from db.repository.tg_user_repo import TGUserRepository

logger = logging.getLogger(__name__)


class ACLMiddleware(BaseMiddleware):
    """Middleware to check access rights to the bot."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]] | None:
        logger.debug('ACLMiddleware called')

        try:
            user: User | None = data.get('event_from_user')
            logger.debug(
                f'ACLMiddleware:'
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

            user_from_db = await tg_user_repo.get_user(user)
            is_super_admin = user.id in config.bot.admins
            logger.debug(f'{user.id=}:{is_super_admin=}')

            if not user_from_db:
                role: Role = Role.ADMIN if is_super_admin else Role.VISITOR
                is_active = is_super_admin
                user_from_db = await tg_user_repo.upsert_user(
                    telegram_user=user,
                    role=role,
                    is_active=is_active,
                )
                logger.info(
                    f'New user created:'
                    f' {user.id} (role={role.value}, active={is_active})'
                )
            elif user_from_db:
                if is_super_admin and (
                    not user_from_db.is_active
                    or user_from_db.role != Role.ADMIN.value
                ):
                    await tg_user_repo.upsert_user(
                        telegram_user=user,
                        role=Role.ADMIN,
                        is_active=True,
                    )
                    user_from_db.is_active = True
                    user_from_db.role = Role.ADMIN.value
                    logger.info(
                        f'Super-admin {user.id} role updated to ADMIN'
                    )
            if not user_from_db.is_active:
                if isinstance(event, Message):
                    await event.answer(
                        text='⛔️ Доступ к боту ограничен.'
                        ' Обратитесь к администратору.',
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        text='⛔️ Доступ к боту ограничен.', show_alert=True
                    )
                logger.info(f'User {user.id} is not active')
                return None

            data['role'] = user_from_db.role
            data['is_admin'] = user_from_db.role == Role.ADMIN.value
            logger.debug(
                f'Setting data[is_admin]={data["is_admin"]}'
                f' (role={user_from_db.role})'
            )

            if (
                user_from_db.first_name != user.first_name
                or user_from_db.username != user.username
            ):
                await tg_user_repo.update_user_profile(
                    telegram_user=user,
                )
            logger.debug(f'{user_from_db.is_active=}')
            return await handler(event, data)
        except Exception as e:
            logger.exception(f'💥 ACLMiddleware crashed: {e}')
            return await handler(event, data)
