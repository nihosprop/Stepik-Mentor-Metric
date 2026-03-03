import json
import logging

from datetime import UTC, datetime, timedelta

from dishka.integrations.taskiq import FromDishka, inject

from db.repository.course_repo import CourseRepo
from db.repository.mentor_reply_repo import MentorReplyRepo
from db.repository.stepik_user_repo import StepikUserRepo
from infrastructure.di.providers.redis import RedisCache
from infrastructure.stepik.client import StepikAPIClient

from .broker import broker
from .mixins import MyScheduledTask

logger = logging.getLogger(__name__)


@broker.task
@inject(patch_module=True)
async def poll_stepik_courses(
    stepik_client: FromDishka[StepikAPIClient],
    course_repo: FromDishka[CourseRepo],
    stepik_user_repo: FromDishka[StepikUserRepo],
    mentor_reply_repo: FromDishka[MentorReplyRepo],
    redis_cache: FromDishka[RedisCache],
) -> None:
    logger.info('Polling Stepik courses ON')

    courses_ids_cache = await redis_cache.smembers('courses_ids')  # type: ignore
    if not courses_ids_cache:
        active_ids = set(map(str, await course_repo.get_ids_active_courses()))
        if not active_ids:
            logger.info('No active courses in DB')
            return
        await redis_cache.sadd('courses_ids', *active_ids)  # type: ignore
        await redis_cache.expire('courses_ids', 3600)

    mentors_ids_cache = await redis_cache.smembers('users_ids')  # type: ignore
    if not mentors_ids_cache:
        logger.info('No mentors_ids in Redis, fetching from DB')
        mentors_ids = set(map(str, await stepik_user_repo.get_ids_mentors()))
        if mentors_ids:
            await redis_cache.sadd('users_ids', *mentors_ids)  # type: ignore
            await redis_cache.expire('users_ids', 3600)
        else:
            logger.info('No active mentor IDs found in DB')

    for course_id in courses_ids_cache:
        time_key = f'time:course:{course_id}'
        last_time_str: str = await redis_cache.get(time_key)

        if last_time_str:
            last_time = datetime.fromisoformat(last_time_str)
        else:
            last_time = datetime.now(UTC) - timedelta(days=1)
            logger.info(
                f'First start for course {course_id}.'
                f' Parsing from: {last_time}'
            )

        new_last_time = last_time
        page = 1

        while True:
            response = await stepik_client.get_comments(course_id, page=page)

            if (
                not response
                or 'comments' not in response
                or not response['comments']
            ):
                break

            found_old_on_this_page = False

            for comment in response['comments']:
                comment_time = datetime.fromisoformat(
                    comment['time'].replace('Z', '+00:00')
                )

                if comment_time > last_time:
                    logger.info(
                        f'NEW_COMMENT:'
                        f'{json.dumps(comment, indent=2, ensure_ascii=False)}'
                    )
                    await mentor_reply_repo.upsert_reply(
                        course_id=course_id,
                        comment_id=comment['id'],
                        mentor_id=comment['user'],
                        parent_comment_id=comment['parent'],
                        comment_created_at=comment_time,
                        is_mentor_reply=True,
                    )
                    new_last_time = max(new_last_time, comment_time)
                else:
                    found_old_on_this_page = True

            if found_old_on_this_page or not response.get('meta', {}).get(
                'has_next'
            ):
                break
            page += 1

        await redis_cache.set(time_key, new_last_time.isoformat())


STATIC_TASKS = [
    MyScheduledTask(
        task_name=poll_stepik_courses.task_name,
        schedule_id='2f779070-5683-4d6e-bc51-3e5e95175564',
        cron='* * * * *',
    ),
]
