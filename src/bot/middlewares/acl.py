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
        user: User | None = data.get('event_from_user')
        if not user or not isinstance(user, User):
            return await handler(event, data)

        container: AsyncContainer = data['dishka_container']
        config: Config = await container.get(Config)
        tg_user_repo: TGUserRepository = await container.get(TGUserRepository)
        user_from_db = await tg_user_repo.get_user(user)

        if not user_from_db:
            is_super_admin = user.id in config.bot.admins
            role: Role = Role.ADMIN if is_super_admin else Role.VISITOR
            is_active = is_super_admin

            user_from_db = await tg_user_repo.upsert_user(
                telegram_user=user,
                role=role,
                is_active=is_active,
            )

        if not user_from_db.is_active:
            if isinstance(event, Message):
                await event.answer(
                    '⛔️ Доступ к боту ограничен. Обратитесь к администратору.'
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    text='⛔️ Доступ к боту ограничен.', show_alert=True
                )
            return None

        data['role'] = user_from_db.role
        data['is_admin'] = user_from_db.role == Role.ADMIN

        if (
            user_from_db.first_name != user.first_name
            or user_from_db.username != user.username
        ):
            await tg_user_repo.update_user_profile(
                telegram_user=user,
            )

        return await handler(event, data)
