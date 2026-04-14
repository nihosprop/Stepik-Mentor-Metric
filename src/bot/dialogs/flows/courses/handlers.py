import logging

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select
from dishka.integrations.aiogram_dialog import FromDishka, inject

from db.repository.course_repo import CourseRepo
from infrastructure.di.providers.redis import RedisCache
from infrastructure.stepik.client import StepikAPIClient

logger = logging.getLogger(__name__)


@inject
async def on_course_selected(
    _clbk: CallbackQuery,
    _widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    logger.debug('Entry')

    dialog_manager.dialog_data['course_id'] = int(item_id)
    await dialog_manager.next()

    logger.debug('Exit')


@inject
async def on_delete_course(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    course_repo: FromDishka[CourseRepo],
) -> None:
    logger.debug('Entry')

    await course_repo.delete_course(
        course_id=dialog_manager.dialog_data['course_id']
    )
    await clbk.answer(
        '✅ Курс успешно удален!\nМожете продолжить.', show_alert=True
    )
    logger.debug('Exit')


@inject
async def correct_link_to_course(
    _msg: Message,
    _widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
    stepik_client: FromDishka[StepikAPIClient],
) -> None:
    logger.debug('Entry')

    course_id = int(text)
    course_title = await stepik_client.get_course_title(course_id=course_id)

    if course_title:
        dialog_manager.dialog_data['course_id'] = course_id
        dialog_manager.dialog_data['course_title'] = course_title
        await dialog_manager.next()

    logger.debug(f'Course title: {course_title or "Not found course"}')
    logger.debug('Exit')


async def error_link_to_course(
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
async def add_course_to_db(
    clbk: CallbackQuery,
    _button: Button,
    dialog_manager: DialogManager,
    course_repo: FromDishka[CourseRepo],
    redis_cache: FromDishka[RedisCache],
) -> None:
    logger.debug('Entry')

    course_id = dialog_manager.dialog_data['course_id']
    course_title = dialog_manager.dialog_data['course_title']

    try:
        await course_repo.upsert_course(
            course_id=course_id, title=course_title
        )
        await redis_cache.delete('courses_ids')
        logger.info(f'Cleared courses cache after adding course {course_id}')
        await clbk.answer(
            f'✅ Курс {course_title}r добавлен!\nМожете продолжить.',
            show_alert=True,
        )
    except Exception as e:
        logger.error(f'Error adding course {course_id}: {e}', exc_info=True)
        await clbk.answer(
            f'❌ Ошибка при добавлении курса {course_id}.\n'
            'Повторите или обратитесь к разработчику.',
            show_alert=True,
        )
        return

    logger.debug('Exit')
