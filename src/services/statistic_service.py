import logging

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from core.main_config import Config
from db.repository.statistic_repo import StatisticRepo

logger = logging.getLogger(__name__)


@dataclass
class StatisticService:
    stats_repo: StatisticRepo
    config: Config

    async def get_daily_report_text(self) -> str:
        """Final report for yesterday - with efficiency
        and speed (from the archive)."""
        yesterday = datetime.now(UTC).date() - timedelta(days=1)
        rows = await self.stats_repo.get_report_from_stats(yesterday)
        header = f'🏆 <b>Итоги дня: {yesterday.strftime("%d.%m.%Y")}</b>'
        return self._format_advanced_report(rows, header)

    async def get_report_by_date_text(self, year: int, month: int) -> str:
        """Final report for the month."""
        rows = await self.stats_repo.get_monthly_stats(year, month)
        header = f'📈 <b>Текущий месяц: {month:02d}.{year}</b>'

        return self._format_advanced_report(rows, header, is_monthly=True)

    async def get_monthly_report_text(self, prev_month: bool = True) -> str:
        """
        Args:
            prev_month (bool, optional): Whether the previous month
        Returns:
            str: text.
        """
        now = datetime.now(UTC)

        if prev_month:
            first_day_this_month = now.replace(day=1)
            last_day_prev_month = first_day_this_month - timedelta(days=1)

            year = last_day_prev_month.year
            month = last_day_prev_month.month
        else:
            year = now.year
            month = now.month

        return await self.get_report_by_date_text(year=year, month=month)

    async def aggregate_stats_period(
        self,
        start_date: date,
        end_date: date | None = None,
    ) -> None:
        """Aggregates statistics for an arbitrary period."""

        end_date = end_date or datetime.now(UTC).date()

        logger.info(f'Start aggregation {start_date} - {end_date}')

        current = start_date
        days_processed = 0

        while current <= end_date:
            try:
                await self.stats_repo.calculate_and_save_daily_stats(current)
                days_processed += 1
                logger.debug(f'Aggregated stats for {current}')
            except Exception as e:
                logger.error(f'Failed to aggregate stats for {current}: {e}')

            current += timedelta(days=1)

        logger.info(f'Aggregated {days_processed} days of statistics')

    @staticmethod
    def _format_simple_report(rows: Sequence, header: str) -> str:
        """
        Format statistics report based on the given rows and header.

        Args:
            rows (Sequence): A sequence of tuples containing
                the full name of the mentor, the title of the course,
                and the number of replies made by the mentor.
            header (str): Report header.

        Returns:
            str: Formatted report.
        """
        logger.debug('Generating simple report.')
        if not rows:
            return f'{header}\n\nАктивности менторов не зафиксировано. 📭'

        msg = [header, '']
        current_course = ''
        total_replies = 0

        for row in rows:
            if row.course_title != current_course:
                current_course = row.course_title
                msg.append(f'📘 Курс: {current_course}')

            msg.append(f'🔹{row.full_name}: {row.replies_count} отв.')
            total_replies += row.replies_count

        msg.append(f'\n📈 Всего ответов: {total_replies}')
        return '\n'.join(msg)

    @staticmethod
    def _format_advanced_report(
        rows: Sequence, header: str, is_monthly: bool = False
    ) -> str:
        """
        Format statistics report based on the given rows and header.
        """
        logger.debug('Generating advanced report.')
        if not rows:
            return '📭 Нет архивных данных за прошедший месяц.'

        msg = [header, '']
        current_course = ''
        for row in rows:
            if row.course_title != current_course:
                current_course = row.course_title
                msg.append(f'\n📘 <b>Курс: {current_course}</b>')

            # Index calc
            # (for the month we calculate from the amounts,
            # for the day we take the ready)
            if is_monthly:
                perf_idx = (
                    (row.total_h**2 / row.total_t) if row.total_t > 0 else 0
                )
                replies = row.total_h
            else:
                perf_idx = row.help_index
                replies = row.replies_count

            speed = f'{int(row.avg_delay // 60)}м' if row.avg_delay else 'н/д'

            msg.append(
                f' └ <b>{row.full_name}</b>\n'
                f'   КПД: <b>{perf_idx:.1f}</b> | Отв: {replies} | ⚡️ {speed}'
            )
        return '\n'.join(msg)
