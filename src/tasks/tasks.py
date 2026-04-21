import asyncio
import logging
import os
import uuid

from datetime import UTC, date, datetime, timedelta

from aiogram import Bot
from aiogram.types import FSInputFile
from dishka.integrations.taskiq import FromDishka, inject

from core.main_config import Config
from db.repository.course_repo import CourseRepo
from db.repository.reply_repo import ReplyRepo
from db.repository.statistic_repo import StatisticRepo
from db.repository.stepik_user_repo import StepikUserRepo
from db.repository.tg_user_repo import TGUserRepository
from infrastructure.ai.ai_client import GeminiCommentEvaluator
from infrastructure.di.providers.redis import RedisCache
from infrastructure.stepik.client import StepikAPIClient
from services.statistic_service import StatisticService

from .broker import broker
from .mixins import MyScheduledTask

logger = logging.getLogger(__name__)
ai_logger = logging.getLogger('ai.mentor.replies')

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
    ai_client: FromDishka[GeminiCommentEvaluator],
) -> None:
    lock_key = 'task:poll_stepik_courses:lock'
    lock_ttl = 600
    lock_acquired = await redis_cache.set(lock_key, '1', nx=True, ex=lock_ttl)

    if not lock_acquired:
        logger.warning(
            '⚠️ Previous poll_task still running, skipping this execution'
        )
        return

    try:
        logger.debug('Polling Stepik courses ON')

        try:
            courses_ids_cache = await redis_cache.smembers('courses_ids')  # type: ignore
            logger.debug(f'Courses IDs from cache: {courses_ids_cache}')
        except Exception as e:
            logger.error(f'Redis connection error: {e}')
            return

        if not courses_ids_cache:
            logger.info('No active courses in cache')
            active_ids = set(
                map(str, await course_repo.get_ids_active_courses())
            )
            logger.debug(f'Getting active courses from DB: {active_ids}')
            if not active_ids:
                logger.warning('No active courses in DB - task will exit')
                return
            await redis_cache.sadd('courses_ids', *active_ids)  # type: ignore
            await redis_cache.expire('courses_ids', 3600)

        mentor_ids_from_db = await stepik_user_repo.get_ids_mentors()
        mentors_ids_cache = set(map(str, mentor_ids_from_db))
        logger.debug(
            f'Loaded {len(mentors_ids_cache)} mentors directly from DB'
        )

        if not mentors_ids_cache:
            logger.warning('No active mentor IDs found in DB - task will exit')
            return

        logger.debug(f'{mentors_ids_cache=}')

        for course_id_str in courses_ids_cache:
            course_id = int(course_id_str)
            time_key = f'time:course:{course_id}'
            last_time_str: str = await redis_cache.get(time_key)
            logger.debug(f'Last Time from cache:{last_time_str=}')

            now = datetime.now(UTC)
            if last_time_str:
                last_time = datetime.fromisoformat(last_time_str).astimezone(
                    UTC
                )
            else:
                days_back = config.tasks.initial_poll_days
                last_time: datetime = datetime.now(UTC) - timedelta(
                    days=days_back
                )
                logger.info(
                    f'Cold start for course {course_id}. '
                    f'Parsing from: {last_time} ({days_back} days back)'
                )
            if last_time > now + timedelta(hours=1):
                logger.warning(
                    f'Future last_time detected for course {course_id}:'
                    f' {last_time}. Resetting to initial_poll_days.'
                )
                last_time = now - timedelta(
                    days=config.tasks.initial_poll_days
                )
                await redis_cache.set(time_key, last_time.isoformat(), ex=3600)

            new_last_time = last_time
            page = 1

            while True:
                logger.debug(
                    f'Polling start in page {page} for course {course_id}'
                )
                await redis_cache.expire(lock_key, lock_ttl)
                response = await stepik_client.get_comments(
                    course_id, page=page
                )
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

                    if comment.get('thread') == 'solutions':
                        ai_logger.info(
                            f'Is solutions thread. Comment is not '
                            f'processed.'
                            f'link_to_comment: {
                                await stepik_client.get_comment_url(
                                    comment_id=comment["id"]
                                )
                            }'
                        )
                        continue

                    if comment_time > last_time:
                        # logger.debug(
                        #     f'NEW_COMMENT: {comment["id"]=},'
                        #     f' {comment["parent"]=}'
                        # )

                        author_id = comment['user']
                        author_username = await stepik_client.get_username(
                            author_id
                        )

                        if not author_username:
                            author_username = f'User_{author_id}'

                        author_id_str = str(comment['user'])
                        is_mentor = author_id_str in mentors_ids_cache

                        is_useful_comment = False
                        if not is_mentor:
                            await stepik_user_repo.upsert_user(
                                stepik_user_id=author_id,
                                full_name=author_username,
                                is_mentor=False,
                            )
                            is_useful_comment = (
                                await ai_client.is_meaningful_question(
                                    comment['text'].strip()
                                )
                            )

                            ai_logger.info(
                                f'link_to_comment: {
                                    await stepik_client.get_comment_url(
                                        comment_id=comment["id"]
                                    )
                                }'
                            )

                        await reply_repo.upsert_reply_with_mentor_check(
                            course_id=course_id,
                            comment_id=int(comment['id']),
                            author_id=author_id,
                            parent_comment_id=comment['parent'],
                            comment_created_at=comment_time,
                            is_useful_comment=is_useful_comment,
                        )
                        new_last_time = max(new_last_time, comment_time)
                    else:
                        found_old_on_this_page = True

                if found_old_on_this_page or not response.get('meta', {}).get(
                    'has_next'
                ):
                    break
                page += 1
                logger.debug(
                    f'Polling end in page {page} for course {course_id}'
                )
            try:
                await redis_cache.set(time_key, new_last_time.isoformat())
            except Exception as e:
                logger.error(
                    f'Failed to save last_time for course {course_id}: {e}'
                )
            if not last_time_str:
                aggregation_flag = f'initial_aggregation_flag:{course_id}'

                if not await redis_cache.get(aggregation_flag):
                    logger.info(
                        f'Cold Running aggregation for course {course_id}...'
                    )
                    start_date = (
                        datetime.now(UTC)
                        - timedelta(days=config.tasks.initial_poll_days)
                    ).date()
                    end_date = datetime.now(UTC).date()

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
    except Exception as e:
        logger.error(
            f'❌ Error during course polling: {type(e).__name__}: {e}',
            exc_info=True,
        )
    finally:
        await redis_cache.delete(lock_key)
        logger.debug('Task lock released')


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
    statistic_service: FromDishka[StatisticService],
    tg_user_repo: FromDishka[TGUserRepository],
) -> None:
    """
    Sends daily statistics report to bot admins, admins, and visitors.

    Args:
        bot (FromDishka[Bot]): Bot instance.
        config (FromDishka[Config]): Config instance.
        statistic_service (FromDishka[StatisticService]):
         StatisticService instance.
        tg_user_repo (FromDishka[TGUserRepository]): TG user repository.
    Returns:
        None
    """

    report_text = await statistic_service.get_daily_report_text()

    recipients = set(config.bot.admins)

    admins = await tg_user_repo.get_all_admins()
    recipients.update(admin.telegram_id for admin in admins)

    visitors = await tg_user_repo.get_all_visitors()
    recipients.update(visitor.telegram_id for visitor in visitors)

    for recipient_id in recipients:
        try:
            await bot.send_message(chat_id=recipient_id, text=report_text)
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f'Failed to send report to {recipient_id}: {e}')


@broker.task
@inject(patch_module=True)
async def sends_last_month_stats(
    bot: FromDishka[Bot],
    config: FromDishka[Config],
    statistic_service: FromDishka[StatisticService],
    tg_user_repo: FromDishka[TGUserRepository],
) -> None:
    logger.debug('Entry')

    report_text = await statistic_service.get_global_report_text(
        prev_month=True
    )
    file_path = await statistic_service.save_report_to_file(
        report_text=report_text, report_type='last_month'
    )

    now = datetime.now(UTC)
    last_day_prev_month = now.replace(day=1) - timedelta(days=1)
    prev_month_str = last_day_prev_month.strftime('%m.%Y')

    try:
        document = FSInputFile(file_path, filename=os.path.basename(file_path))

        recipients = set(config.bot.admins)

        admins = await tg_user_repo.get_all_admins()
        recipients.update(admin.telegram_id for admin in admins)

        visitors = await tg_user_repo.get_all_visitors()
        recipients.update(visitor.telegram_id for visitor in visitors)

        for recipient_id in recipients:
            try:
                await bot.send_document(
                    chat_id=recipient_id,
                    document=document,
                    caption=f'📊 Подробная за {prev_month_str}',
                )
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(
                    f'Failed to send report to {recipient_id}: {e}',
                    exc_info=True,
                )

    except Exception as e:
        logger.error(
            f'Failed to send stats to recipients: {e}',
            exc_info=True,
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f'Temporary file {file_path} deleted successfully')


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
        cron='5 0 * * *',
    ),
    MyScheduledTask(
        task_name=sends_daily_stats.task_name,
        schedule_id=_schedule_id(task_name=sends_daily_stats.task_name),
        cron='10 0 * * *',
    ),
    MyScheduledTask(
        task_name=sends_last_month_stats.task_name,
        schedule_id=_schedule_id(task_name=sends_last_month_stats.task_name),
        cron='15 0 1 * *',
    ),
]
