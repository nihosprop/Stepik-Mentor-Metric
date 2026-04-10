# src/bot/dialogs/common/errors.py
"""
Global error handlers for aiogram-dialog exceptions.
Compatible with aiogram 3.x, dishka auto_inject=True, and strict type checkers (ty/mypy).
"""
import logging
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, Update
from aiogram_dialog.api.exceptions import UnknownState

logger = logging.getLogger(__name__)


def register_error_handlers(dp: Dispatcher) -> None:
    """
    Registers global error handlers for aiogram-dialog.
    Must be called AFTER setup_dialogs(dp) in main.py.
    """

    @dp.errors(UnknownState)
    async def handle_unknown_state(
        exception: UnknownState,
        **kwargs: Any,
    ) -> bool:
        """
        Recovers from UnknownState by clearing broken FSM context.
        Gracefully handles missing state/event due to early middleware failures.
        """
        # aiogram 3.x passes context via kwargs in error handlers
        event: Update | None = kwargs.get('event')
        state: FSMContext | None = kwargs.get('state')
        bot: Bot | None = kwargs.get('bot')

        if not event or not bot:
            logger.warning('Event or Bot not available in error handler context')
            return False

        payload = event.event
        if not isinstance(payload, Message | CallbackQuery) or not payload.from_user:
            logger.debug(f'Skipping recovery for unsupported event type: {type(payload)}')
            return False

        user_id = payload.from_user.id
        logger.warning(f'🔄 UnknownState recovered | user={user_id} | err={exception}')

        # 🧹 Graceful state clearing (state may be None if error occurs early in chain)
        if state:
            try:
                await state.clear()
                logger.debug(f'Cleared FSM state for user {user_id}')
            except Exception as e:
                logger.error(f'Failed to clear FSM state: {e}')
        else:
            logger.debug(f'State not available for user {user_id} (relying on TTL cleanup)')

        # 📩 Notify user (type-safe for ty)
        text = '⚠️ Интерфейс обновлён. Отправьте /start для продолжения.'
        try:
            if isinstance(payload, Message):
                await payload.answer(text=text)
            elif isinstance(payload, CallbackQuery) and payload.message:
                await payload.message.answer(text=text)
            else:
                # Fallback: direct message if answer() is not applicable
                await bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            logger.debug(f'Failed to notify user {user_id}: {e}')

        # ✅ Mark error as handled
        return True