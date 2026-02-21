import logging

from aiogram import Router
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from dishka.integrations.aiogram_dialog import FromDishka, inject

from infrastructure.stepik.client import StepikAPIClient

start_router = Router()

logger = logging.getLogger(__name__)


@inject
async def correct_link_to_mentor(
    msg: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
    stepik_client: FromDishka[StepikAPIClient],
) -> None:
    logger.debug('Entry')

    stepik_user_name = await stepik_client.get_username(user_id=int(text))
    logger.debug(f'Stepik username: {stepik_user_name or "Not found user"}')

    logger.debug('Exit')


async def error_link_to_mentor(
    msg: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
) -> None:
    logger.debug('Entry')

    await msg.delete()

    # TODO: write down the msg_id and delete it on the next update
    await msg.answer(f'Вы ввели некорректную ссылку:\n'
                     f'<i>{msg.text}</i>\n')

    logger.debug('Exit')
