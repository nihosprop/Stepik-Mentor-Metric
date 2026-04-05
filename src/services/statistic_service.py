import logging
import os

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

    @staticmethod
    async def save_report_to_file(report_text: str, report_type: str) -> str:
        base_dir = '/app/logs'
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{report_type}_{date_str}.md'
        file_path = os.path.join(base_dir, filename)
        report_for_file = report_text.replace('<b>', '').replace('</b>', '')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_for_file)

        return file_path

    async def get_daily_report_text(self) -> str:
        """Final report for yesterday - with efficiency and
         speed (from the archive).

        Args:
            self
        Returns:
            str: text
        """
        yesterday = datetime.now(UTC).date() - timedelta(days=1)
        rows = await self.stats_repo.get_report_from_stats(yesterday)
        header = f'🏆 <b>Итоги дня: {yesterday.strftime("%d.%m.%Y")}</b>'
        return self._format_advanced_report(rows, header)

    async def get_report_by_date_text(
        self, perf: str, year: int, month: int
    ) -> str:
        """Final report for the month."""
        rows = await self.stats_repo.get_monthly_stats(year, month)
        header = f'📈 {perf}: {month:02d}.{year}'

        return self._format_advanced_report(rows, header, is_monthly=True)

    async def get_general_report_text(
        self, prev_month: bool = True
    ) -> str | None:
        """
        Retrieves a general report for the current month or the previous month.

        Args:
            prev_month (bool, optional): Whether to retrieve the report
             for the previous month. Defaults to True.
        Returns:
            str: The general report text.
        """
        now = datetime.now(UTC)

        if prev_month:
            first_day_this_month = now.replace(day=1)
            last_day_prev_month = first_day_this_month - timedelta(days=1)
            start_date = last_day_prev_month.replace(day=1).date()
            end_date = last_day_prev_month.date()
            header = (
                f'🏆 <b>Прошедший месяц\n'
                f' {start_date.strftime("%d.%m.%Y")}'
                f' - {end_date.strftime("%d.%m.%Y")}</b>'
            )
        else:
            start_date = now.replace(day=1).date()
            end_date = now.date()
            header = (
                f'🏆 <b>Текущий месяц\n'
                f'{start_date.strftime("%d.%m.%Y")}'
                f' - {end_date.strftime("%d.%m.%Y")}</b>'
            )

        await self.aggregate_stats_period(start_date, end_date)

        rows = await self.stats_repo.get_general_stats(start_date, end_date)
        return self._format_general_report(rows, header)

    async def get_monthly_detailed_report_text(
        self, prev_month: bool = True
    ) -> str:
        """
        Args:
            prev_month (bool, optional): Flag for previous month
        Returns:
            str: text.
        """
        now = datetime.now(UTC)
        perf = 'Текущий месяц'
        if prev_month:
            perf = 'Прошедший месяц'
            first_day_this_month = now.replace(day=1)
            last_day_prev_month = first_day_this_month - timedelta(days=1)

            start_date = last_day_prev_month.replace(day=1).date()
            end_date = last_day_prev_month.date()

            year = last_day_prev_month.year
            month = last_day_prev_month.month
        else:
            start_date = now.replace(day=1).date()
            end_date = now.date()

            year = now.year
            month = now.month

        await self.aggregate_stats_period(start_date, end_date)

        return await self.get_report_by_date_text(
            perf=perf, year=year, month=month
        )

    async def get_global_report_text(self, prev_month: bool = True) -> str:
        general_report_text = await self.get_general_report_text(
            prev_month=prev_month
        )
        monthly_report_text = await self.get_monthly_detailed_report_text(
            prev_month=prev_month
        )
        return f'{general_report_text}\n\n{monthly_report_text}'

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
    def _calculate_percentile_indices(rows: Sequence) -> list[int | None]:
        """
        Calculates a composite index (0–100) based on percentiles
        speed and activity.
        Formula: Index = (Score_speed + Score_activity) / 2
        """

        valid_data = []
        for i, row in enumerate(rows):

            avg_delay = row.avg_delay
            replies = row.total_h

            if replies is None:
                replies = row.replies_count or 0

            if avg_delay is not None and replies > 0:
                valid_data.append(
                    {'idx': i, 'avg_delay': avg_delay, 'replies': replies}
                )

        n = len(valid_data)

        if n == 0:
            return [None] * len(rows)
        if n == 1:
            indices: list[int | None]  = [None] * len(rows)
            indices[valid_data[0]['idx']] = 100
            return indices

        sorted_speed = sorted(valid_data, key=lambda x: x['avg_delay'])
        speed_ranks = {
            item['idx']: rank + 1 for rank, item in enumerate(sorted_speed)
        }

        sorted_activity = sorted(
            valid_data, key=lambda x: x['replies'], reverse=True
        )
        activity_ranks = {
            item['idx']: rank + 1 for rank, item in enumerate(sorted_activity)
        }

        indices: list[int | None] = [None] * len(rows)
        for item in valid_data:
            i = item['idx']
            score_speed = (n - speed_ranks[i]) / (n - 1) * 100
            score_activity = (n - activity_ranks[i]) / (n - 1) * 100
            indices[i] = round((score_speed + score_activity) / 2)

        return indices

    def _format_general_report(self,
        rows: Sequence,
        header: str,
    ) -> str | None:
        """
        Format general statistics report (aggregated across all courses).
        """
        logger.debug('Generating general report.')
        if not rows:
            return None

        indices = self._calculate_percentile_indices(rows)
        msg = [header, '=== Общая статистика по менторам ===']

        for row, idx in zip(rows, indices, strict=True):
            perf_idx = (row.total_h**2 / row.total_t) if row.total_t > 0 else 0
            replies = row.total_h

            speed_display = f'{idx}⚡' if idx is not None else 'н/д'
            msg.append(
                f'👤 <b>{row.full_name}</b>\n'
                f'  └ КПД:'
                f' <b>{perf_idx:.1f}</b> | Отв: {replies} | ⚡️ {speed_display}'
            )
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
            return '📭 Нет архивных данных.'

        indices = StatisticService._calculate_percentile_indices(rows)

        msg = [header, '=== Статистика по курсам ===']
        current_course = ''
        for row, idx in zip(rows, indices, strict=True):
            if row.course_title != current_course:
                current_course = row.course_title
                msg.append(f'\n📘 <b>Курс: {current_course}</b>')

            if is_monthly:
                perf_idx = (
                    (row.total_h**2 / row.total_t) if row.total_t > 0 else 0
                )
                replies = row.total_h
            else:
                perf_idx = row.help_index
                replies = row.replies_count

            speed_display = f'{idx}⚡' if idx is not None else 'н/д'
            msg.append(
                f' └👤 <b>{row.full_name}</b>\n'
                f'    └ КПД:'
                f' <b>{perf_idx:.1f}</b> | Отв: {replies} | ⚡️ {speed_display}'
            )
        return '\n'.join(msg)
