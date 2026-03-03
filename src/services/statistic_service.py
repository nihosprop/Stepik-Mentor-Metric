from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta

from db.repository.statistic_repo import StatisticRepo


@dataclass
class StatisticService:
    repo: StatisticRepo

    async def get_yesterday_report_text(self) -> str:
        """Prepares a report for yesterday's full day for distribution."""
        yesterday = datetime.now(UTC).date() - timedelta(days=1)
        start = datetime.combine(yesterday, time.min, tzinfo=UTC)
        end = datetime.combine(yesterday, time.max, tzinfo=UTC)

        rows = await self.repo.get_stats_for_period(start, end)
        return self._format_report(
            rows, f'Итоговый отчет за {yesterday.strftime("%d.%m.%Y")}'
        )

    async def get_live_report_text(self) -> str:
        """Prepares operational report for today
         (from 00:00 to the current moment)."""
        now = datetime.now(UTC)
        rows = await self.repo.get_current_day_stats()
        header = (f'📊 Оперативный отчет за {now.strftime("%d.%m.%Y")}\n'
                  f'🕒 _Актуально на {now.strftime("%H:%M")} UTC_')
        return self._format_report(rows, header)

    @staticmethod
    def _format_report(rows: Sequence, header: str) -> str:
        """Internal method for rendering text (Presentation Layer)."""
        if not rows:
            return f'{header}\n\nАктивности менторов не зафиксировано. 📭'

        msg = [header, '']
        current_course = ''
        total_replies = 0

        for row in rows:
            if row.course_title != current_course:
                current_course = row.course_title
                msg.append(f'📘 Курс: {current_course}')

            msg.append(f'  ▪️ {row.full_name}: {row.replies_count} отв.')
            total_replies += row.replies_count

        msg.append(f'\n📈 Всего ответов: {total_replies}')
        return '\n'.join(msg)
