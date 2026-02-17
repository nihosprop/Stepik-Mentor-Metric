import logging

from dataclasses import dataclass

from aiogram.types import User as TelegramUser
from sqlalchemy import delete, exists, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.telegram_user import User

logger = logging.getLogger(__name__)