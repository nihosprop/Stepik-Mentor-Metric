import logging
import os

from datetime import UTC, datetime, timedelta

from aiogram import Bot
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram_dialog import FromDishka, inject

from bot.dialogs.flows.statistic.states import StatisticSG
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
            caption=f'📊 Подробная(Текущий месяц)-{datetime.now(UTC).date()}',
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
    bot: FromDishka[Bot],
) -> None:
    logger.debug('Entry')

    now = datetime.now(UTC)
    last_day_prev_month = now.replace(day=1) - timedelta(days=1)
    prev_month_str = last_day_prev_month.strftime('%m.%Y')

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
            caption=f'📊 Подробная статистика за {prev_month_str}',
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
async def send_last_month_general_stats(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
) -> None:
    logger.debug('Entry')

    logger.info(f'The user {clbk.from_user.id} requested statistics')

    if isinstance(clbk.message, Message):
        await clbk.message.edit_text('⏳ Формирую отчет...')
    else:
        return

    report = await statistic_service.get_general_report_text(prev_month=True)
    if clbk.message and report:
        await clbk.message.answer(text=report)
    else:
        await clbk.answer(
            text='📭 Нет данных для статистики.', show_alert=True
        )
        return

    await dialog_manager.switch_to(
        state=StatisticSG.general, show_mode=ShowMode.DELETE_AND_SEND
    )

    logger.debug('Exit')


@inject
async def sent_current_month_general_report(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    statistic_service: FromDishka[StatisticService],
) -> None:
    logger.debug('Entry')

    logger.info(f'The user {clbk.from_user.id} requested statistics')

    if isinstance(clbk.message, Message):
        await clbk.message.edit_text('⏳ Формирую отчет...')
    else:
        return

    report = await statistic_service.get_general_report_text(prev_month=False)
    if clbk.message and report:
        await clbk.message.answer(text=report)
    else:
        await clbk.answer(
            text='📭 Нет данных для статистики.', show_alert=True
        )
        return

    await dialog_manager.switch_to(
        state=StatisticSG.general, show_mode=ShowMode.DELETE_AND_SEND
    )

    logger.debug('Exit')
