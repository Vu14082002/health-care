from src.config import config
from src.core.cache.redis_backend import RedisBackend

redis_working = RedisBackend(config.REDIS_URL_WORKING_TIME)
