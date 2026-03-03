from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from db.repository.course_repo import CourseRepo
from db.repository.reply_repo import ReplyRepo
from db.repository.stepik_user_repo import StepikUserRepo
from db.repository.tg_user_repo import TGUserRepository


class RepositoryProvider(Provider):
    """
    Repository Provider
    """
    scope = Scope.REQUEST

    @provide
    def tg_user_repo(self, session: AsyncSession) -> TGUserRepository:
        """
        Telegram user repository

        Args:
            session: AsyncSession
        Returns:
            UserRepository
        """
        return TGUserRepository(session=session)

    @provide
    def stepik_user_repo(self, session: AsyncSession) -> StepikUserRepo:
        """
        Stepik user repository

        Args:
            session: AsyncSession
        Returns:
            StepikUserRepo
        """
        return StepikUserRepo(session=session)

    @provide
    def course_repo(self, session: AsyncSession) -> CourseRepo:
        """
        Course repository

        Args:
            session: AsyncSession

        Returns: CourseRepo
        """
        return CourseRepo(session=session)

    @provide
    def mentor_reply_repo(self, session: AsyncSession) -> ReplyRepo:
        """
        Mentor reply repository

        Args:
            session: AsyncSession

        Returns: ReplyRepo
        """
        return ReplyRepo(session=session)
