import asyncio
import logging
import uuid

from datetime import UTC, date, datetime, timedelta

from aiogram import Bot
from dishka.integrations.taskiq import FromDishka, inject

from core.main_config import Config
from db.repository.course_repo import CourseRepo
from db.repository.reply_repo import ReplyRepo
from db.repository.statistic_repo import StatisticRepo
from db.repository.stepik_user_repo import StepikUserRepo
from infrastructure.di.providers.redis import RedisCache
from infrastructure.stepik.client import StepikAPIClient
from services.statistic_service import StatisticService

from .broker import broker
from .mixins import MyScheduledTask

logger = logging.getLogger(__name__)

# TODO: remove `patch_module=True`


# OPT: Too many arguments-Ruff
# OPT: Too many branches-Ruff
# OPT: Too many statements-Ruff
@broker.task
@inject(patch_module=True)
async def poll_stepik_courses(
    stepik_client: FromDishka[StepikAPIClient],
    course_repo: FromDishka[CourseRepo],
    stepik_user_repo: FromDishka[StepikUserRepo],
    stats_service: FromDishka[StatisticService],
    reply_repo: FromDishka[ReplyRepo],
    redis_cache: FromDishka[RedisCache],
    config: FromDishka[Config],
) -> None:
    logger.info('Polling Stepik courses ON')

    try:
        courses_ids_cache = await redis_cache.smembers('courses_ids')  # type: ignore
        logger.debug(f'Courses IDs from cache: {courses_ids_cache}')
    except Exception as e:
        logger.error(f'Redis connection error: {e}')
        return
    
    if not courses_ids_cache:
        logger.info('No active courses in cache')
        active_ids = set(map(str, await course_repo.get_ids_active_courses()))
        logger.info(f'Getting active courses from DB: {active_ids}')
        if not active_ids:
            logger.warning('No active courses in DB - task will exit')
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
        logger.debug(f'Last Time from cache:{last_time_str=}')

        if last_time_str:
            last_time = datetime.fromisoformat(last_time_str)
        else:
            days_back = config.tasks.initial_poll_days
            last_time: datetime = datetime.now(UTC) - timedelta(days=days_back)
            logger.info(
                f'Cold start for course {course_id}. '
                f'Parsing from: {last_time} ({days_back} days back)'
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
                comment_time: datetime = datetime.fromisoformat(
                    comment['time'].replace('Z', '+00:00')
                )

                if comment_time > last_time:
                    logger.debug(
                        f'NEW_COMMENT: {comment["id"]=}, {comment["parent"]=}')

                    author_id = comment['user']
                    author_username = await stepik_client.get_username(
                        author_id
                    )

                    if not author_username:
                        author_username = f'User_{author_id}'

                    author_id_str = str(comment['user'])
                    is_mentor = author_id_str in mentors_ids_cache

                    if not is_mentor:
                        await stepik_user_repo.upsert_user(
                            stepik_user_id=author_id,
                            full_name=author_username,
                            is_mentor=False,
                        )
                        logger.debug(
                            f'Auto-registered student'
                            f' {author_id}: {author_username}'
                        )

                    # TODO: transfer to service `await reply_repo.upsert_reply`
                    await reply_repo.upsert_reply(
                        course_id=course_id,
                        comment_id=comment['id'],
                        author_id=author_id,
                        parent_comment_id=comment['parent'],
                        comment_created_at=comment_time,
                        is_mentor_reply=is_mentor,
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

        if not last_time_str:
            aggregation_flag = f'initial_aggregation_flag:{course_id}'

            if not await redis_cache.get(aggregation_flag):
                logger.info(
                    f'Cold start for course {course_id}.'
                    f' Running aggregation...'
                )

                start_date = (
                    datetime.now(UTC)
                    - timedelta(days=config.tasks.initial_poll_days)
                ).date()
                end_date = datetime.now(UTC).date() - timedelta(days=1)

                if start_date <= end_date:
                    await stats_service.aggregate_stats_period(
                        start_date=start_date, end_date=end_date
                    )
                    logger.info(
                        f'Init aggregation completed for'
                        f' {start_date} - {end_date}'
                    )

                await redis_cache.set(aggregation_flag, 'true')
                logger.info(f'Aggregation flag set for course:{course_id}')


@broker.task
@inject(patch_module=True)
async def aggregate_daily_stats(
    stat_repo: FromDishka[StatisticRepo],
    redis_cache: FromDishka[RedisCache],
) -> None:
    yesterday: date = datetime.now(UTC).date() - timedelta(days=1)

    try:
        await stat_repo.calculate_and_save_daily_stats(yesterday)
        logger.info(f'Daily stats aggregated for {yesterday}')
    except Exception as e:
        logger.error(
            f'❌ Failed to aggregate stats for {yesterday}: {e}', exc_info=True
        )
        course_ids = await redis_cache.smembers('courses_ids')  # type: ignore
        if not course_ids:
            logger.debug('No courses in cache, skipping reconciliation')
            return

        for course_id in course_ids:
            time_key = f'time:course:{course_id}'
            last_time_str: str | None = await redis_cache.get(time_key)

            if not last_time_str:
                logger.debug(f'No last_time for course {course_id}, skipping')
                continue

            last_time = datetime.fromisoformat(last_time_str)
            now = datetime.now(UTC)
            gap = now - last_time

            if gap > timedelta(hours=25):
                logger.warning(
                    f'Gap detected for course {course_id}: '
                    f'{gap} since last poll'
                )

                start_date = last_time.date()
                end_date = yesterday

                current = start_date
                while current <= end_date:
                    try:
                        await stat_repo.calculate_and_save_daily_stats(current)
                        current += timedelta(days=1)
                    except Exception as e:
                        logger.error(
                            f'Failed to fill gap for {current}: {e}',
                            exc_info=True,
                        )


# TODO: add checking exists courses and mentors?
@broker.task
@inject(patch_module=True)
async def sends_daily_stats(
    bot: FromDishka[Bot],
    config: FromDishka[Config],
    stat_service: FromDishka[StatisticService],
) -> None:
    report_text = await stat_service.get_daily_report_text()

    # TODO: remove duplicate code 2
    for admin_id in config.bot.admins:
        try:
            await bot.send_message(chat_id=admin_id, text=report_text)
            await asyncio.sleep(1)
        except Exception as e:
            logging.error(f'Failed to send report to {admin_id}: {e}')


@broker.task
@inject(patch_module=True)
async def sends_month_stats(
    bot: FromDishka[Bot],
    config: FromDishka[Config],
    stat_service: FromDishka[StatisticService],
) -> None:
    report_text = await stat_service.get_monthly_report_text()

    # TODO: remove duplicate code 3
    for admin_id in config.bot.admins:
        try:
            await bot.send_message(chat_id=admin_id, text=report_text)
            await asyncio.sleep(2)
        except Exception as e:
            logging.error(f'Failed to send report to {admin_id}: {e}')


# TODO: move _schedule_id
def _schedule_id(task_name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, task_name))

# TODO: move settings
STATIC_TASKS = [
    MyScheduledTask(
        task_name=poll_stepik_courses.task_name,
        schedule_id=_schedule_id(task_name=poll_stepik_courses.task_name),
        interval=180,
    ),
    MyScheduledTask(
        task_name=aggregate_daily_stats.task_name,
        schedule_id=_schedule_id(aggregate_daily_stats.task_name),
        cron='2 0 * * *',
    ),
    MyScheduledTask(
        task_name=sends_daily_stats.task_name,
        schedule_id=_schedule_id(task_name=sends_daily_stats.task_name),
        cron='10 0 * * *',
    ),
    MyScheduledTask(
        task_name=sends_month_stats.task_name,
        schedule_id=_schedule_id(task_name=sends_month_stats.task_name),
        cron='10 0 1 * *',
    ),
]
