from aiogram.enums import ParseMode
from dynaconf import Dynaconf
from pydantic import BaseModel, SecretStr


class BotConfig(BaseModel):
    bot_token: SecretStr
    parse_mode: ParseMode


class LogsConfig(BaseModel):
    log_level: str


class RedisConfig(BaseModel):
    pass


class PostgresConfig(BaseModel):
    pass


class StepikConfig(BaseModel):
    pass


class Config(BaseModel):
    bot: BotConfig
    logs: LogsConfig
    redis: RedisConfig
    postgres: PostgresConfig


settings = Dynaconf(
    envvar_prefix=False,
    load_dotenv=True,
    settings_file='settings.toml',
    environments=True,
)

print(settings.bot)


def get_config() -> Config:
    pass
