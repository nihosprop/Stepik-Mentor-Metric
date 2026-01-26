from aiogram.enums import ParseMode
from dynaconf import Dynaconf
from pydantic import BaseModel, Field, SecretStr


class BotConfig(BaseModel):
    token: SecretStr
    parse_mode: ParseMode


class LogsConfig(BaseModel):
    log_level: str = Field(pattern='^(DEBUG|INFO)$')


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


settings = Dynaconf(
    envvar_prefix=False,
    load_dotenv=True,
    settings_files=['settings.toml'],
    environments=True,
    env_switcher='ENV_FOR_DYNACONF',
)


def get_config() -> Config:
    bot = BotConfig(
        token=settings.bot_token, parse_mode=settings.bot.parse_mode
    )

    logs = LogsConfig(log_level=settings.logs.log_level)

    redis = RedisConfig(
        host=settings.get(
            'redis_host', settings.get('redis.host', 'localhost')
        ),
        port=settings.redis.port,
        password=settings.get('redis_password'),
    )

    postgres = PostgresConfig(
        name=settings.postgres.name,
        host=settings.get(
            'postgres_host', settings.get('postgres.host', 'localhost')
        ),
        port=settings.postgres.port,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )

    stepik = StepikConfig(
        stepik_client_id=settings.stepik_client_id,
        stepik_client_secret=settings.stepik_client_secret,
    )

    return Config(
        bot=bot, logs=logs, redis=redis, postgres=postgres, stepik=stepik
    )
