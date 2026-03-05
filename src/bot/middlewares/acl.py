import logging

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from dishka import AsyncContainer

from core.main_config import Config

logger = logging.getLogger(__name__)


class ACLMiddleware(BaseMiddleware):
    """Middleware to check access rights to the bot."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]] | None:
        user = data.get('event_from_user')
        if not user:
            return await handler(event, data)

        container: AsyncContainer = data['dishka_container']
        config = await container.get(Config)

        if user.id in config.bot.admins:
            data['is_admin'] = True
            return await handler(event, data)

        # TODO: достать список юзеров из db

        if isinstance(event, Message):
            if event.from_user:
                logger.warning(f'Attempt to start without rights: '
                               f'{event.from_user.full_name}:'
                               f'{event.from_user.id}')
            await event.answer('У вас нет доступа к этому боту. ⛔️')
        return None
