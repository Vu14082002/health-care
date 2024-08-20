# -*- coding: utf-8 -*-
import asyncio
import json
import traceback
from typing import Any, Dict, Union
from urllib.parse import urlparse

from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.cluster import RedisCluster

from src.lib.logger import logger


class Cache:

    def __init__(self, redis: Union[Redis, RedisCluster, None] = None) -> None:
        self.redis = redis
        self.url = None
        self.kw: Dict = {}

    @classmethod
    def config(cls, url, **kw):
        _class = cls(redis=None)
        _class.url = url
        _class.kw = kw
        return _class

    def connect(self):
        pool = ConnectionPool.from_url(url=self.url, **self.kw)
        redis = Redis(connection_pool=pool)
        parsed = urlparse(self.url)
        url_replaced = parsed._replace(
            netloc="{}:{}@{}:{}".format(
                parsed.username, "******", parsed.hostname, parsed.port
            )
        )
        logger.debug(f"Redis connected: {url_replaced.geturl()}")
        self.redis = redis

    async def check_connect(self):
        await self.redis.ping()

    def get_redis(self) -> Union[Redis, RedisCluster, None]:
        return self.redis

    def get_key(self, filter: Dict, *args, **kwargs) -> str:
        _keys = list(filter.keys())
        _keys.sort()
        _key_items = [f"{k}.{filter[k]}" for k in _keys]
        return ":".join(_key_items)

    async def command(self, function, key, *args, **kwargs):
        _func = getattr(self.redis, function)
        return await _func(key, *args, **kwargs)

    async def set(self, key: str, data: Any, ttl: float = -1, *args, **kwargs) -> None:
        if not self.redis:
            raise Exception("Redis not config")
        if isinstance(data, dict):
            data = json.dumps(data)
        if ttl == -1:
            await self.redis.set(key, data)
        else:
            await self.redis.set(key, data, ex=ttl)

    async def get(self, key: str, *args, **kwargs) -> Any:
        if not self.redis:
            raise Exception("Redis not config")
        data = await self.redis.get(key)
        if not data:
            return data
        if isinstance(data, bytes):
            data = data.decode()
        return data

    async def set_list(
        self, key: str, data: list, ttl: float = -1, *args, **kwargs
    ) -> None:
        if not self.redis:
            raise Exception("Redis not config")
        async with self.redis.pipeline() as pipeline:
            for item in data:
                if isinstance(item, dict) or isinstance(item, list):
                    item = json.dumps(item, ensure_ascii=False)
                await pipeline.lpush(key, item)
            await pipeline.execute()

    async def get_list(self, key: str, *args, **kwargs) -> list:
        if not self.redis:
            raise Exception("Redis not config")
        data = await self.redis.lrange(key, 0, -1)

        async def format_data(item):
            try:
                # load data type is list
                return json.loads(item)
            except Exception:
                # load data str, int,..
                return item

        _tasks = [format_data(i) for i in data]
        data = await asyncio.gather(*_tasks)
        return data

    async def hset(self, key: str, hset_key: Any, data: Any, *args, **kwargs) -> None:
        if not self.redis:
            raise Exception("Redis not config")
        _hset_val = None
        if isinstance(filter, dict):
            _hset_val = self.get_key(filter)
        if isinstance(filter, filter):
            _filter_dict = dict(filter)
            _hset_val = _filter_dict.get(hset_key)
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        await self.redis.hset(key, str(_hset_val), data)

    async def hget(self, key: str, hset_val: str, *args, **kwargs):
        if not self.redis:
            raise Exception("Redis not config")
        return await self.redis.hget(key, hset_val)

    async def hget_all(self, key: str, *args, **kwargs):
        if not self.redis:
            raise Exception("Redis not config")
        try:
            return await self.redis.hgetall(key)
        except Exception:
            traceback.print_exc()
            return None
