from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dishka import Provider, Scope, provide

from core.main_config import Config


class BotProvider(Provider):
    @provide(scope=Scope.APP)
    def bot(self, config: Config) -> Bot:
        return Bot(
            token=config.bot.token,
            default=DefaultBotProperties(parse_mode=config.bot.parse_mode)
        )