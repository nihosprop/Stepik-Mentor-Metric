from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import AuthorReply


@dataclass
class ReplyRepo:
    session: AsyncSession
    # OPT: Too many arguments(6 > 5)-Ruff
    async def upsert_reply(
        self,
        course_id: int,
        comment_id: str,
        author_id: int,
        parent_comment_id: int | None,
        comment_created_at: datetime,
        is_mentor_reply: bool,
    ) -> None:
        """Saves the metadata of the author's response if
        data not in the database."""

        stmt = (
            insert(AuthorReply)
            .values(
                comment_id=comment_id,
                course_id=course_id,
                author_id=author_id,
                parent_comment_id=parent_comment_id,
                comment_created_at=comment_created_at,
                is_mentor_reply=is_mentor_reply,
            )
            .on_conflict_do_update(
                index_elements=['comment_id'],
                set_={
                    'course_id': course_id,
                    'author_id': author_id,
                    'parent_comment_id': parent_comment_id,
                    'comment_created_at': comment_created_at,
                    'is_mentor_reply': is_mentor_reply,
                },
            )
        )
        await self.session.execute(stmt)
