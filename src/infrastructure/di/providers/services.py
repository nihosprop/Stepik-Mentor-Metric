import aiohttp

from dishka import Provider, Scope, provide

from core.main_config import Config
from db.repository.statistic_repo import StatisticRepo
from infrastructure.ai.ai_client import GeminiCommentEvaluator
from services.statistic_service import StatisticService


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def stats_service(
        self, repo: StatisticRepo, config: Config
    ) -> StatisticService:
        return StatisticService(
            stats_repo=repo,
            config=config,
        )

    @provide(scope=Scope.APP)
    def gemini_evaluator(
        self, config: Config, session: aiohttp.ClientSession
    ) -> GeminiCommentEvaluator:
        return GeminiCommentEvaluator(
            api_key=config.ai.gemini_api_key,
            session=session,
        )
