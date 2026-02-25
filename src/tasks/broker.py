from dishka import make_async_container
from dishka.integrations.taskiq import setup_dishka
from taskiq_redis import RedisStreamBroker

from core.main_config import main_config
from infrastructure.di.providers import PROVIDERS

broker = RedisStreamBroker(
    url=f'redis://{main_config.redis.host}:{main_config.redis.port}'
)

container = make_async_container(*PROVIDERS)
setup_dishka(container=container, broker=broker)
