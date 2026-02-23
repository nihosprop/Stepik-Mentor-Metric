import logging

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select
from dishka.integrations.aiogram_dialog import FromDishka, inject

from db.repository.stepik_user_repo import StepikUserRepo
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


@inject
async def add_mentor_to_db(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    stepik_user_repo: FromDishka[StepikUserRepo],
) -> None:
    logger.debug('Entry')

    stepik_user_id = dialog_manager.dialog_data['mentor_id']
    mentor_name = dialog_manager.dialog_data['stepik_username']

    await stepik_user_repo.upsert_user(
        stepik_user_id=stepik_user_id,
        full_name=mentor_name,
        is_mentor=True,
    )
    await clbk.answer(
        f'✅ Ментор {mentor_name} успешно добавлен!\nМожете продолжить.',
        show_alert=True,
    )
    logger.debug('Exit')


@inject
async def on_mentor_selected(
    _clbk: CallbackQuery,
    _widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    logger.debug('Entry')

    dialog_manager.dialog_data['mentor_id'] = int(item_id)
    await dialog_manager.next()

    logger.debug('Exit')


@inject
async def on_delete_mentor(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    stepik_user_repo: FromDishka[StepikUserRepo],
) -> None:
    logger.debug('Entry')

    await stepik_user_repo.delete_user(dialog_manager.dialog_data['mentor_id'])
    await clbk.answer(
        '✅ Ментор успешно удален!\nМожете продолжить.', show_alert=True
    )
    logger.debug('Exit')
