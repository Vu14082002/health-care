import pickle
from typing import Any, List

import redis.asyncio as aioredis
import ujson

from src.config import config
from src.core.cache.base import BaseBackend

# redis = aioredis.from_url(url=config.REDIS_URL)


class RedisBackend(BaseBackend):
    def __init__(self, redis_url: str = config.REDIS_URL) -> None:
        if redis_url:
            self.redis = aioredis.from_url(url=redis_url)
        else:
            self.redis = aioredis.from_url(url=redis_url)
        super().__init__()

    async def get_all_keys_by_pattern(self, pattern: str) -> Any:
        return await self.redis.keys(pattern)

    async def get_all_keys(self) -> List[str]:
        keys = []
        async for key in self.redis.scan_iter():
            keys.append(key.decode('utf-8'))
        return keys

    async def get(self, key: str) -> Any:
        result = await self.redis.get(key)
        if not result:
            return
        try:
            return ujson.loads(result.decode("utf8"))
        except UnicodeDecodeError:
            return pickle.loads(result)

    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        if isinstance(response, dict):
            response = ujson.dumps(response)
        elif isinstance(response, object):
            response = pickle.dumps(response)

        await self.redis.set(name=key, value=response, ex=ttl)

    async def delete_startswith(self, value: str) -> None:
        async for key in self.redis.scan_iter(f"{value}::*"):
            await self.redis.delete(key)

    async def delete(self, key: str) -> None:
        print("Deleting key: ", key)
        await self.redis.delete(key)
