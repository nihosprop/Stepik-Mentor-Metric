import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.flows.statistic.states import StatisticSG

logger = logging.getLogger(__name__)

async def switch_to_statistic(
    _clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
) -> None:
    logger.debug('Entry')

    await dialog_manager.start(state=StatisticSG.start)

    logger.debug('Exit')
