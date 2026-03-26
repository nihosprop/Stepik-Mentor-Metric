import logging

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram_dialog import FromDishka, inject

from services.statistic_service import StatisticService

logger = logging.getLogger(__name__)


@inject
async def send_current_month(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
    bot: FromDishka[Bot],
) -> None:
    logger.debug('Entry')

    report = await statistic_service.get_monthly_report_text(prev_month=False)

    await bot.send_message(chat_id=clbk.from_user.id, text=report)
    logger.debug('Exit')


@inject
async def send_general_stats(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
) -> None:
    logger.debug('Entry')

    report = await statistic_service.get_general_report_text(prev_month=False)
    if report:
        if clbk.message:
            await clbk.message.answer(text=report)
        return
    await clbk.answer(text='📭 Нет данных для статистики.', show_alert=True)

    logger.debug('Exit')


@inject
async def send_last_month_stats(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
    bot: FromDishka[Bot],
) -> None:
    logger.debug('Entry')

    report = await statistic_service.get_general_report_text(prev_month=True)
    if report:
        await bot.send_message(chat_id=clbk.from_user.id, text=report)
        return
    await clbk.answer(text='📭 Нет данных для статистики.', show_alert=True)

    logger.debug('Exit')


@inject
async def send_last_month(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
) -> None:
    logger.debug('Entry')

    report = await statistic_service.get_monthly_report_text()
    await clbk.answer(report)

    logger.debug('Exit')
