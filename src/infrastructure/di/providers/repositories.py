
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from db.repository.user_repo import UserRepository


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session=session)
