import logging

from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import exists, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.stepik_user import StepikUser

logger = logging.getLogger(__name__)


@dataclass
class StepikUserRepo:
    session: AsyncSession

    async def _user_exists(self, stepik_user_id: int) -> bool | None:
        stmt = select(exists().where(StepikUser.user_id == stepik_user_id))
        return await self.session.scalar(stmt)

    async def promote_to_mentor(
        self, stepik_user_id: int, full_name: str
    ) -> None:
        stmt = (
            insert(StepikUser)
            .values(
                user_id=stepik_user_id, full_name=full_name, is_mentor=True
            )
            .on_conflict_do_update(
                index_elements=['user_id'],
                set_={
                    'is_mentor': True,
                    'full_name': full_name,
                },
            )
        )
        await self.session.execute(stmt)

    async def upsert_user(
        self, stepik_user_id: int, full_name: str, is_mentor: bool = False
    ) -> None:
        insert_stmt = insert(StepikUser).values(
            user_id=stepik_user_id, full_name=full_name, is_mentor=is_mentor
        )
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['user_id'],
            set_={'full_name': full_name},
        )
        await self.session.execute(upsert_stmt)
        logger.debug(f'Upserted Stepik user {stepik_user_id}')

    async def delete_user(self, stepik_user_id: int) -> None:
        stmt = (
            update(StepikUser)
            .where(StepikUser.user_id == stepik_user_id)
            .values(is_mentor=False)
        )
        await self.session.execute(stmt)
        logger.debug(f'Deleted Stepik user {stepik_user_id}')

    async def get_stepik_user(self, stepik_user_id: int) -> StepikUser | None:
        """Gets a user object by ID."""
        stmt = select(StepikUser).where(StepikUser.user_id == stepik_user_id)
        return await self.session.scalar(stmt)

    async def get_all_mentors(self) -> Sequence[StepikUser]:
        """Returns a list of all users who have is_mentor=True"""
        stmt = select(StepikUser).where(StepikUser.is_mentor)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_ids_mentors(self) -> Sequence[int]:
        """Returns a list of all mentor IDs."""
        stmt = select(StepikUser.user_id).where(StepikUser.is_mentor)
        result = await self.session.execute(stmt)
        return result.scalars().all()
