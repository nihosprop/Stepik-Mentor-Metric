from dataclasses import dataclass

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import MentorReply


@dataclass
class MentorReplyRepo:
    session: AsyncSession

    async def upsert_reply(self, comment_id: str,
                           course_id: int,
                           mentor_id: int,
                           parent_comment_id: int,
                           comment_created_at: str) -> None:
        """Saves the metadata of the mentor's response if
        data not in the database."""

        stmt = (
            insert(MentorReply)
            .values(
                comment_id=comment_id,
                course_id=course_id,
                mentor_id=mentor_id,
                parent_comment_id=parent_comment_id,
                comment_created_at=comment_created_at,
            )
            .on_conflict_do_update()
        )
        await self.session.execute(stmt)
