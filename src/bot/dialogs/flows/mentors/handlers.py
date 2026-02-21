import logging

from aiogram import Router
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from dishka.integrations.aiogram_dialog import FromDishka, inject

from infrastructure.stepik.client import StepikAPIClient

start_router = Router()

logger = logging.getLogger(__name__)


@inject
async def correct_link_to_mentor(
    _msg: Message,
    _widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
    stepik_client: FromDishka[StepikAPIClient],
) -> None:
    logger.debug('Entry')

    mentor_id = int(text)

    stepik_username = await stepik_client.get_username(user_id=mentor_id)
    logger.debug(f'Stepik username: {stepik_username or "Not found user"}')
    if stepik_username:
        dialog_manager.dialog_data['mentor_id'] = mentor_id
        dialog_manager.dialog_data['stepik_username'] = stepik_username
        await dialog_manager.next()

    logger.debug('Exit')


async def error_link_to_mentor(
    msg: Message,
    _widget: ManagedTextInput,
    _dialog_manager: DialogManager,
    _error: ValueError,
) -> None:
    logger.debug('Entry')

    await msg.delete()

    # TODO: write down the msg_id and delete it on the next update
    await msg.answer(f'Вы ввели некорректную ссылку:\n<i>{msg.text}</i>\n')

    logger.debug('Exit')
