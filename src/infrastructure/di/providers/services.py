from dishka import Provider, Scope, provide

from core.main_config import Config
from db.repository.statistic_repo import StatisticRepo
from services.statistic_service import StatisticService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def stats_service(
        self, repo: StatisticRepo, config: Config
    ) -> StatisticService:
        return StatisticService(
            stats_repo=repo,
            config=config,
        )
