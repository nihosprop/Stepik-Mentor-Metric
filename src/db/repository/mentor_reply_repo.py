from dataclasses import dataclass

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import MentorReply


@dataclass
class MentorReplyRepo:
    session: AsyncSession

    async def upsert_reply(self, reply_data: dict) -> None:
        """Saves the metadata of the mentor's response if
        data not in the database."""

        stmt = (
            insert(MentorReply)
            .values(
                comment_id=reply_data['id'],
                course_id=reply_data['course'],
                mentor_id=reply_data['user'],
                parent_comment_id=reply_data['parent'] or 0,
                stepik_created_at=reply_data['time'],
            )
            .on_conflict_do_update()
        )
        await self.session.execute(stmt)
