
from dishka import Provider, Scope, provide

from core.main_config import Config, main_config


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        return main_config
