import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.dialogs.flows.statistic.states import StatisticSG

logger = logging.getLogger(__name__)
