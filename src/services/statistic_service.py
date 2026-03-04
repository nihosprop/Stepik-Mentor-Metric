from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta

from db.repository.statistic_repo import StatisticRepo


@dataclass
class StatisticService:
    repo: StatisticRepo

    async def get_live_report_text(self) -> str:
        """
        Get operational report for current day.
        Returns:
            str: text.
        """
        now = datetime.now(UTC)
        rows = await self.repo.get_current_day_stats()
        header = (f'📊 <b>Live-статистика</b>\n'
                  f'🕒 {now.strftime("%d.%m.%Y %H:%M")} UTC')
        return self._format_simple_report(rows, header)

    async def get_yesterday_report_text(self) -> str:
        """
        Get operational report for yesterday.
        Returns:
            str: text.
        """
        yesterday = datetime.now(UTC).date() - timedelta(days=1)
        start = datetime.combine(yesterday, time.min, tzinfo=UTC)
        end = datetime.combine(yesterday, time.max, tzinfo=UTC)

        rows = await self.repo.get_stats_for_period(start, end)
        return self._format_simple_report(
            rows, f'Итоговый отчет за {yesterday.strftime("%d.%m.%Y")}'
        )


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
