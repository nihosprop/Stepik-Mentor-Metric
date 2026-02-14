import aiohttp

from dishka import Provider, Scope, provide

from core.main_config import Config
from infrastructure.di.providers.redis import RedisCache
from infrastructure.stepik.client import StepikAPIClient


class StepikProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_stepik_client(
        self, config: Config, cache: RedisCache, session: aiohttp.ClientSession
    ) -> StepikAPIClient:
        return StepikAPIClient(
            client_id=config.stepik.stepik_client_id.get_secret_value(),
            client_secret=config.stepik.stepik_client_secret.get_secret_value(),
            redis_cache=cache,
            session=session,
        )
