import logging

from typing import Any

from aiogram.types import User
from aiogram_dialog import DialogManager, ShowMode
from dishka.integrations.aiogram_dialog import FromDishka, inject

from services.statistic_service import StatisticService

logger = logging.getLogger(__name__)


@inject
async def get_current_month_general_stats(
    dialog_manager: DialogManager,
    event_from_user: User,
    statistic_service: FromDishka[StatisticService],
    **kwargs,
) -> dict[str, Any]:
    logger.debug('Entry')
    
    report = dialog_manager.dialog_data['current_month_general_report']
    
    logger.debug('Exit')

    return {'stats': report}


