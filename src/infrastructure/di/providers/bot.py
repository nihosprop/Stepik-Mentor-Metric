from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dishka import Provider, Scope, provide

from core.main_config import Config


class BotProvider(Provider):
    @provide(scope=Scope.APP) # Создается один раз на весь процесс
    def bot(self, config: Config) -> Bot:
        # Провайдер сам берет токен из конфига
        return Bot(
            token=config.bot.token,
            default=DefaultBotProperties(parse_mode=config.bot.parse_mode)
        )