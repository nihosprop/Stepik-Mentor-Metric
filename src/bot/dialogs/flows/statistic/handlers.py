import logging
import os

from datetime import datetime

from aiogram import Bot
from aiogram.types import CallbackQuery, FSInputFile
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram_dialog import FromDishka, inject

from services.statistic_service import StatisticService

logger = logging.getLogger(__name__)


@inject
async def send_current_month_detailed_stats(
    clbk: CallbackQuery,
    _button: Button,
    _dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
    bot: FromDishka[Bot],
) -> None:
    # TODO: use clbk.message, methods on the stack must return str | None
    logger.debug('Entry')

    logger.info(f'The user {clbk.from_user.id} requested statistics')
    report = await statistic_service.get_monthly_detailed_report_text(
        prev_month=False
    )

    file_path = await statistic_service.save_report_to_file(
        report, 'current_month'
    )

    try:
        document = FSInputFile(file_path, filename=os.path.basename(file_path))

        await bot.send_document(
            chat_id=clbk.from_user.id,
            document=document,
            caption=f'📊 Подробная(Текущий месяц)-{datetime.now().date()}',
        )
    except Exception as e:
        logger.error(
            f'Failed to send stats to admin {clbk.from_user.id}: {e}',
            exc_info=True,
        )

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f'Temporary file {file_path} deleted successfully')

    logger.debug('Exit')


@inject
async def send_last_month_detailed_stats(
    clbk: CallbackQuery,
    _button: Button,
    _dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
    bot: FromDishka[Bot]
) -> None:
    logger.debug('Entry')

    logger.info(f'The user {clbk.from_user.id} requested statistics')
    report = await statistic_service.get_monthly_detailed_report_text(
        prev_month=True
        )

    file_path = await statistic_service.save_report_to_file(
        report, 'last_month'
    )

    try:
        document = FSInputFile(file_path, filename=os.path.basename(file_path))

        await bot.send_document(
            chat_id=clbk.from_user.id,
            document=document,
            caption=f'📊 Подробная(Прошедший месяц)-{datetime.now().date()}',
        )
    except Exception as e:
        logger.error(
            f'Failed to send stats to admin {clbk.from_user.id}: {e}',
            exc_info=True,
        )

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f'Temporary file {file_path} deleted successfully')

    logger.debug('Exit')


@inject
async def send_current_month_general_stats(
    clbk: CallbackQuery,
    _button: Button,
    _dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
) -> None:
    logger.debug('Entry')

    logger.info(f'The user {clbk.from_user.id} requested statistics')
    report = await statistic_service.get_general_report_text(prev_month=False)
    if report:
        if clbk.message:
            await clbk.message.answer(text=report)
        return
    await clbk.answer(text='📭 Нет данных для статистики.', show_alert=True)

    logger.debug('Exit')


@inject
async def send_last_month_general_stats(
    clbk: CallbackQuery,
    _button: Button,
    _dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
) -> None:
    logger.debug('Entry')

    logger.info(f'The user {clbk.from_user.id} requested statistics')
    report = await statistic_service.get_general_report_text(prev_month=True)
    if report:
        if clbk.message:
            await clbk.message.answer(text=report)
        return
    await clbk.answer(text='📭 Нет данных для статистики.', show_alert=True)
    logger.debug('Exit')
