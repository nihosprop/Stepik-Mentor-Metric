from typing import Any

from aiogram.enums import ParseMode
from dynaconf import Dynaconf
from pydantic import BaseModel, Field, SecretStr


class TaskConfig(BaseModel):
    initial_poll_days: int = Field(default=1, ge=0, le=365)
    polling_interval_sec: int = Field(default=3, ge=1, le=900)


class AIConfig(BaseModel):
    gemini_api_key: SecretStr


class BotConfig(BaseModel):
    token: str
    admins: list[int]
    parse_mode: ParseMode


class LogsConfig(BaseModel):
    dict_config: dict[str, Any]


class StepikConfig(BaseModel):
    stepik_client_id: SecretStr
    stepik_client_secret: SecretStr


class RedisConfig(BaseModel):
    host: str
    port: int
    password_secret: SecretStr | None = Field(default=None, min_length=7)
    decode_responses: bool

    @property
    def password(self) -> str | None:
        if self.password_secret is None:
            return None
        return self.password_secret.get_secret_value()


class PostgresConfig(BaseModel):
    driver: str
    user: str
    password: SecretStr = Field(min_length=7)
    host: str
    port: int
    name: str

    def get_dsn(self) -> str:
        return (
            f'{self.driver}'
            f'://{self.user}:{self.password.get_secret_value()}'
            f'@{self.host}:{self.port}/{self.name}'
        )


class Config(BaseModel):
    bot: BotConfig
    logs: LogsConfig
    redis: RedisConfig
    postgres: PostgresConfig
    stepik: StepikConfig
    tasks: TaskConfig
    ai: AIConfig


_settings = Dynaconf(
    envvar_prefix=False,
    load_dotenv=True,
    settings_files=['settings.toml'],
    environments=True,
    env_switcher='ENV_FOR_DYNACONF',
    merge_enabled=True,
)


def _get_config() -> Config:
    bot = BotConfig(
        token=_settings.bot_token,
        admins=list(map(int, _settings.bot_admins.split(' '))),
        parse_mode=_settings.bot.parse_mode,
    )

    logs = LogsConfig(dict_config=_settings.logs.dict_config.to_dict())

    redis = RedisConfig(
        host=_settings.get(
            'redis_host', _settings.get('redis.host', 'localhost')
        ),
        port=_settings.redis.port,
        password_secret=_settings.get('redis_password'),
        decode_responses=_settings.redis.decode_responses,
    )

    postgres = PostgresConfig(
        name=_settings.postgres.name,
        host=_settings.get(
            'postgres_host', _settings.get('postgres.host', 'localhost')
        ),
        port=_settings.postgres.port,
        user=_settings.postgres_user,
        password=_settings.postgres_password,
        driver=_settings.postgres.driver,
    )

    stepik = StepikConfig(
        stepik_client_id=_settings.stepik_client_id,
        stepik_client_secret=_settings.stepik_client_secret,
    )

    tasks = TaskConfig(
        initial_poll_days=_settings.tasks.initial_poll_days,
        polling_interval_sec=_settings.tasks.polling_interval_sec,
    )
    ai = AIConfig(gemini_api_key=_settings.gemini_api_key)

    return Config(
        bot=bot,
        logs=logs,
        redis=redis,
        postgres=postgres,
        stepik=stepik,
        tasks=tasks,
        ai=ai,
    )


main_config: Config = _get_config()
