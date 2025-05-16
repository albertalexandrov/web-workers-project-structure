from faststream.redis import RedisBroker

from app.settings import settings

from .logging import logger

redis_broker = RedisBroker(f"redis://{settings.redis_host}:{settings.redis_port}", logger=logger)
