from dishka import Provider, Scope, provide

from db.repository.statistic_repo import StatisticRepo
from services.statistic_service import StatisticService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def stats_service(self, repo: StatisticRepo) -> StatisticService:
        return StatisticService(repo=repo)
