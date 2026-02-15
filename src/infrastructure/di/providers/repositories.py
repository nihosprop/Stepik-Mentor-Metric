from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from db.repository.user_repo import UserRepository


class RepositoryProvider(Provider):
    """
    Repository Provider
    """
    @provide(scope=Scope.REQUEST)
    def get_tg_user_repo(self, session: AsyncSession) -> UserRepository:
        """
        Get User Repository
        Args:
            session: AsyncSession
        Returns:
            UserRepository
        """
        return UserRepository(session=session)
