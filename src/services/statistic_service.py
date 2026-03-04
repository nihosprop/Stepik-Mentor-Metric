from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime

from db.repository.statistic_repo import StatisticRepo


@dataclass
class StatisticService:
    stats_repo: StatisticRepo

    async def get_live_report_text(self) -> str:
        """
        Get operational report for current day.
        Returns:
            str: text.
        """
        now = datetime.now(UTC)
        rows = await self.stats_repo.get_current_day_stats()
        header = (
            f'📊 <b>Live-статистика</b>\n'
            f'🕒 {now.strftime("%d.%m.%Y %H:%M")} UTC'
        )
        return self._format_simple_report(rows, header)

    async def get_daily_report_text(self, target_date: date) -> str:
        """Final report for the day - with efficiency
        and speed (from the archive)."""
        rows = await self.stats_repo.get_report_from_stats(target_date)
        header = f'🏆 <b>Итоги дня: {target_date.strftime("%d.%m.%Y")}</b>'
        return self._format_advanced_report(rows, header)

    async def get_monthly_report_text(self, year: int, month: int) -> str:
        """Final report for the month."""
        rows = await self.stats_repo.get_monthly_stats(year, month)
        header = f'📈 <b>Results of the month: {month:02d}.{year}</b>'

        return self._format_advanced_report(rows, header, is_monthly=True)

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
        if not rows:
            return f'{header}\n\nНет архивных данных. 📭'

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
