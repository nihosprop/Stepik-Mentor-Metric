from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from db.repository.stepik_user_repo import StepikUserRepo
from db.repository.user_repo import UserRepository


class RepositoryProvider(Provider):
    """
    Repository Provider
    """

    @provide(scope=Scope.REQUEST)
    def tg_user_repo(self, session: AsyncSession) -> UserRepository:
        """
        Telegram user repository
        Args:
            session: AsyncSession
        Returns:
            UserRepository
        """
        return UserRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def stepik_user_repo(self, session: AsyncSession) -> StepikUserRepo:
        """
        Stepik user repository
        Args:
            session: AsyncSession
        Returns:
            StepikUserRepo
        """
        return StepikUserRepo(session=session)
