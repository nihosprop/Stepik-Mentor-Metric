from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import AuthorReply
from db.models.stepik_user import StepikUser


@dataclass
class ReplyRepo:
    session: AsyncSession

    # OPT: Too many arguments-Ruff
    async def upsert_reply(
        self,
        course_id: int,
        comment_id: int,
        author_id: int,
        parent_comment_id: int | None,
        comment_created_at: datetime,
        is_mentor_reply: bool,
        is_useful_comment: bool = False,
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
                is_useful_comment=is_useful_comment,
            )
            .on_conflict_do_update(
                index_elements=['comment_id'],
                set_={
                    'course_id': course_id,
                    'author_id': author_id,
                    'parent_comment_id': parent_comment_id,
                    'comment_created_at': comment_created_at,
                    'is_mentor_reply': is_mentor_reply,
                    'is_useful_comment': is_useful_comment,
                },
            )
        )
        await self.session.execute(stmt)

    # OPT: Too many arguments-Ruff
    async def upsert_reply_with_mentor_check(
        self,
        course_id: int,
        comment_id: int,
        author_id: int,
        parent_comment_id: int | None,
        comment_created_at: datetime,
        is_useful_comment: bool = False,
    ) -> None:
        stmt = select(StepikUser.is_mentor).where(
            StepikUser.user_id == author_id
        )
        is_mentor = await self.session.scalar(stmt) or False

        await self.upsert_reply(
            course_id,
            comment_id,
            author_id,
            parent_comment_id,
            comment_created_at,
            is_mentor,
            is_useful_comment,
        )
