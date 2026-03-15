from dishka import make_async_container
from dishka.integrations.taskiq import setup_dishka
from taskiq_redis import RedisStreamBroker

from core.logger import setup_logging
from core.main_config import main_config
from infrastructure.di.providers import PROVIDERS

setup_logging()

redis_password = main_config.redis.password
redis_password_str = f':{redis_password}@' if redis_password else ''

broker = RedisStreamBroker(
    url=f'redis://{redis_password_str}{main_config.redis.host}'
        f':{main_config.redis.port}'
)

container = make_async_container(*PROVIDERS)
setup_dishka(container=container, broker=broker)
