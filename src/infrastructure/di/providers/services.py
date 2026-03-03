from dishka import Provider, Scope, provide

from services.statistic_service import StatisticService
from src.db.repository.statistic_repo import StatisticRepo


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def stats_service(self, repo: StatisticRepo) -> StatisticService:
        return StatisticService(repo=repo)
