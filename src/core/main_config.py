from typing import Any

from aiogram.enums import ParseMode
from dynaconf import Dynaconf
from pydantic import BaseModel, Field, SecretStr


class BotConfig(BaseModel):
    token: str
    parse_mode: ParseMode


class LogsConfig(BaseModel):
    dict_config: dict[str, Any]


class StepikConfig(BaseModel):
    stepik_client_id: SecretStr
    stepik_client_secret: SecretStr


class RedisConfig(BaseModel):
    host: str
    port: int
    password: SecretStr | None = Field(default=None, min_length=7)


class PostgresConfig(BaseModel):
    name: str
    host: str
    port: int
    user: str
    password: SecretStr


class Config(BaseModel):
    bot: BotConfig
    logs: LogsConfig
    redis: RedisConfig
    postgres: PostgresConfig
    stepik: StepikConfig


_settings = Dynaconf(
    envvar_prefix=False,
    load_dotenv=True,
    settings_files=['settings.toml'],
    environments=True,
    env_switcher='ENV_FOR_DYNACONF',
)


def _get_config() -> Config:
    bot = BotConfig(
        token=_settings.bot_token, parse_mode=_settings.bot.parse_mode
    )

    logs = LogsConfig(dict_config=_settings.logs.dict_config.to_dict())

    redis = RedisConfig(
        host=_settings.get(
            'redis_host', _settings.get('redis.host', 'localhost')
        ),
        port=_settings.redis.port,
        password=_settings.get('redis_password'),
    )

    postgres = PostgresConfig(
        name=_settings.postgres.name,
        host=_settings.get(
            'postgres_host', _settings.get('postgres.host', 'localhost')
        ),
        port=_settings.postgres.port,
        user=_settings.postgres_user,
        password=_settings.postgres_password,
    )

    stepik = StepikConfig(
        stepik_client_id=_settings.stepik_client_id,
        stepik_client_secret=_settings.stepik_client_secret,
    )

    return Config(
        bot=bot, logs=logs, redis=redis, postgres=postgres, stepik=stepik
    )

main_config: Config = _get_config()
