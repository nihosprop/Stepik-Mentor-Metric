import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button
from dishka import FromDishka

from db.repository.tg_user_repo import TGUserRepository

from .states import StartSG

start_router = Router()

logger = logging.getLogger(__name__)

