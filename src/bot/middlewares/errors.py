import logging

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.api.exceptions import UnknownState

from bot.dialogs.flows.start.states import StartSG

logger = logging.getLogger(__name__)


class DialogResetMiddleware(BaseMiddleware):
    """Middleware to reset dialog stack when UnknownState occurs."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]] | None:
        try:
            return await handler(event, data)
        except UnknownState as e:
            logger.warning(f'UnknownState caught: {e}')

            if await self._reset_dialog_and_notify(event, data):
                return None
            raise e

    @staticmethod
    async def _reset_dialog_and_notify(
        event: TelegramObject, data: dict[str, Any]
    ) -> bool:
        try:
            bot = data.get('bot')
            dialog_manager: DialogManager | None = data.get('dialog_manager')

            if not bot:
                logger.error('Bot not found in data')
                return False

            chat_id = None
            user_id = None

            if isinstance(event, Message) and event.from_user:
                chat_id = event.chat.id
                user_id = event.from_user.id
            elif (
                isinstance(event, CallbackQuery)
                and event.message
                and event.from_user
            ):
                chat_id = event.message.chat.id
                user_id = event.from_user.id

            if not chat_id or not user_id:
                logger.error('Could not extract chat_id or user_id from event')
                return False

            if dialog_manager:
                try:
                    await dialog_manager.start(
                        state=StartSG.start,
                        mode=StartMode.RESET_STACK,
                        show_mode=ShowMode.SEND,
                    )
                    logger.info(f'Reset dialog stack for user {user_id}')
                except Exception as dialog_error:
                    logger.error(f'Error resetting dialog: {dialog_error}')
            else:
                try:
                    if isinstance(bot, Bot):
                        await bot.send_message(
                            chat_id=chat_id,
                            text='Произошла ошибка.'
                                 ' Пожалуйста, нажмите /start.',
                        )
                        logger.info(
                            f'Sent reset notification to user {user_id}'
                        )
                except Exception as msg_error:
                    logger.error(f'Error sending reset message: {msg_error}')

            return True

        except Exception as e:
            logger.error(f'Error in dialog reset: {e}')
            return False
