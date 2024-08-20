# -*- coding: utf-8 -*-
import json
import traceback
from asyncio import Task, current_task
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Dict, List, Optional, Type, Union, Tuple
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from redis.asyncio import Redis  # type: ignore
from redis.asyncio.cluster import RedisCluster  # type: ignore
from sqlalchemy import Delete, Insert, Select, Update, delete, insert, select, update
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Query, defer, load_only
from sqlalchemy.sql import func
from starlette.background import BackgroundTask
from src.lib.cache import Cache
from sqlalchemy.dialects import postgresql
from src.lib.logger import logger
from contextvars import ContextVar, Token
from uuid import uuid4
import asyncio
from sqlalchemy.ext.declarative import declarative_base


def current_time():
    return datetime.now(tz=timezone.utc)


session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context() -> Token:
    return session_context.set(str(uuid4()))


Base = declarative_base()


def deserialize(func):
    """
    The `deserialize` function is a decorator that formats datetime objects in the result of an async
    function to a specific string format.

    :param func: The `func` parameter is a function that will be decorated by the `deserialize`
    decorator
    :return: The `deserialize` function returns a decorated version of the input function `func`.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        _projection = kwargs.get("projection", [])
        _should_load_data = kwargs.get("should_load_data", True)
        _result = await func(*args, **kwargs)
        if not _result:
            return _result

        async def formatter(data: dict):
            for key, value in data.copy().items():
                if isinstance(value, datetime):
                    data[key] = value.strftime("%d/%m/%Y %H:%M:%S")
                if key in _projection and not _should_load_data:
                    del data[key]
            return data

        if isinstance(_result, list):
            _tasks = [formatter(i) for i in _result]
            _result = await asyncio.gather(*_tasks)
        else:
            _result = await formatter(_result)
        return _result

    return wrapper


def _current_task() -> Task:
    task = current_task()
    if not task:
        raise RuntimeError("No currently active asyncio.Task found")
    return task


class PostgresClient(Cache):
    def __init__(
        self,
        model: Type[Base],  # type: ignore
        session: AsyncSession,
        redis: Union[Redis, None] = None,
        *args,
        **kwargs,
    ) -> None:
        super(PostgresClient, self).__init__(redis, *args, **kwargs)
        self.model = model
        self.session = session
        self.redis = redis
        self._table_name = self.model.__tablename__  # type: ignore
        self.executor = ThreadPoolExecutor()

    def get_key(self, query: Select, *args, **kwargs) -> str:  # type: ignore
        string_query = query.compile(dialect=postgresql.dialect())
        _cache_prefix = kwargs.get("cache_prefix")
        if _cache_prefix:
            return f"{self._table_name}.{_cache_prefix}.{string_query}"
        return f"{self._table_name}.{string_query}"

    async def remove_cache(self, cache_prefix: str):
        _key = f"{self._table_name}.{cache_prefix}*"
        if not self.redis:
            raise Exception("Redis not config")
        async with self.redis.pipeline() as pipeline:
            async for k in self.redis.scan_iter(_key):
                pipeline.delete(k)
            await pipeline.execute()

    @deserialize
    async def find_one(
        self,
        filter: Union[Dict, Select],
        session: Optional[AsyncSession] = None,
        projection: List[str] = [],
        should_load_data: bool = True,
        cache: bool = False,
        cache_expire_time: int = 300,
        cache_prefix: str = "all",
        *args,
        **kwargs,
    ) -> Dict | None:
        _result = None
        _query = None
        if isinstance(filter, Select):
            _query = filter.limit(1)
        else:
            _query = select(self.model).filter_by(**filter).limit(1)
        if len(projection):
            columns = [getattr(self.model, i) for i in projection]
            _query = (
                _query.options(load_only(*columns))
                if should_load_data
                else _query.options(
                    *[defer(getattr(self.model, i)) for i in projection]
                )
            )
        if cache:
            logger.debug(f"GET data {self._table_name} from cache")
            _key = self.get_key(_query, cache_prefix=cache_prefix)
            _result = await self.get(_key)
        if not _result:
            if session:
                _obj = await session.execute(_query)
            else:
                async with asyncio.Lock():
                    _obj = await self.session.execute(_query)
            _obj = _obj.scalars().fetchall()
            if len(_obj) == 0:
                return None
            _obj = _obj[0]
            if len(projection):
                if should_load_data:
                    _result = {c: getattr(_obj, c) for c in projection}
                else:
                    _result = {
                        k: v
                        for (k, v) in _obj.__dict__.items()
                        if k != "_sa_instance_state"
                    }
            else:
                _result = _obj if not _obj else _obj.as_dict

            if cache:
                assert cache_expire_time > 0, "Expire time < 0"

                async def _run_execute():
                    _key = self.get_key(_query, cache_prefix=cache_prefix)
                    await self.set(
                        _key, _result, ttl=cache_expire_time, cache_prefix=cache_prefix
                    )

                loop = asyncio.get_event_loop()
                asyncio.run_coroutine_threadsafe(_run_execute(), loop)
        else:
            _result = json.loads(_result)
        return _result

    @deserialize
    async def find(
        self,
        filter: Union[Dict[str, Any], Select],
        session: Optional[AsyncSession] = None,
        projection: List[str] = [],
        should_load_data: bool = True,
        limit: int = 0,
        skip: int = 0,
        cache: bool = False,
        cache_expire_time: int = 300,
        cache_prefix: str = "all",
        *args,
        **kwargs,
    ) -> List[Dict]:
        _result = []
        _query = None
        if isinstance(filter, Select):
            _query = filter if limit == 0 else filter.limit(limit)
            _query = _query if skip == 0 else _query.offset(skip)
        else:
            if limit == 0:
                _query = select(self.model).filter_by(**filter)
            else:
                _query = select(self.model).filter_by(**filter).limit(limit)
            if skip != 0:
                _query = _query.offset(skip)
        if len(projection):
            columns = [getattr(self.model, i) for i in projection]
            _query = (
                _query.options(load_only(*columns))
                if should_load_data
                else _query.options(
                    *[defer(getattr(self.model, i)) for i in projection]
                )
            )
        if cache:
            logger.debug(f"GET data {self._table_name} from cache")
            _key = self.get_key(_query, cache_prefix=cache_prefix)
            _result = await self.get_list(_key)
        if not _result:
            _result = []
            if session:
                _obj = await session.execute(_query)
            else:
                async with asyncio.Lock():
                    _obj = await self.session.execute(_query)
            _obj = _obj.scalars().fetchall()
            if len(projection):
                if should_load_data:
                    for o in _obj:
                        _result.append({c: getattr(o, c) for c in projection})
                else:
                    for item in _obj:
                        item = {
                            k: v
                            for (k, v) in item.__dict__.items()
                            if k != "_sa_instance_state"
                        }
                        _result.append(item)
            else:
                _result = [] if not _obj else [i.as_dict for i in _obj]

            if cache:
                assert cache_expire_time > 0, "Error cache_expire_time < 0"

                async def _run_in_thread():
                    _key = self.get_key(_query, cache_prefix=cache_prefix)
                    await self.redis.delete(_key)
                    await self.set_list(_key, _result, ttl=cache_expire_time)

                loop = asyncio.get_event_loop()
                asyncio.run_coroutine_threadsafe(_run_in_thread(), loop)
        return _result

    async def _iud(self, _orm, session: AsyncSession):
        _orm = _orm.returning(self.model.id)  # type: ignore
        try:
            _result = await session.execute(_orm)
        except Exception as e:
            await session.rollback()
            await session.commit()
            raise Exception(e)
        await session.commit()
        return _result.all()

    async def insert(
        self,
        data: Union[Dict, List[Dict], Insert],
        session: Optional[AsyncSession] = None,
        background: bool = False,
        *args,
        **kwargs,
    ):
        _session = session if session else self.session
        _insert = insert(self.model).values(data) if isinstance(data, dict) else data

        async def func():
            _res = await self._iud(_insert, session=_session)
            if session and session.is_active and background:
                await session.close()
            return _res

        if background:
            try:
                await BackgroundTask(func)()
                return True
            except Exception:
                traceback.print_exc()
                return False
        return await func()

    async def update(
        self,
        filter: Union[Dict, Update],
        data: Dict,
        session: Optional[AsyncSession] = None,
        background: bool = False,
        *args,
        **kwargs,
    ):
        _update = (
            update(self.model).filter_by(**filter).values(data)
            if isinstance(filter, dict)
            else filter
        )

        async def func():
            if session:
                _res = await self._iud(_update, session=session)
            else:
                async with asyncio.Lock():
                    _res = await self._iud(_update, session=self.session)
            if session and session.is_active and background:
                await session.close()
            return _res

        if background:
            try:
                await BackgroundTask(func)()
                return True
            except Exception:
                traceback.print_exc()
                return False
        return await func()

    async def delete(
        self,
        filter: Union[Dict, Delete],
        session: Optional[AsyncSession] = None,
        background: bool = False,
        *args,
        **kwargs,
    ):
        _delete = (
            delete(self.model).filter_by(**filter)
            if isinstance(filter, dict)
            else filter
        )

        async def func():
            if session:
                _res = await self._iud(_delete, session=session)
            else:
                async with asyncio.Lock():
                    _res = await self._iud(_delete, session=self.session)
            if session and session.is_active and background:
                await session.close()
            return _res

        if background:
            try:
                await BackgroundTask(func)()
                return True
            except Exception:
                traceback.print_exc()
                return False
        return await func()

    async def count(
        self,
        filter: Union[Dict, Select],
        session: Optional[AsyncSession] = None,
    ) -> int:
        _session = session if session else self.session
        if isinstance(filter, Select):
            _obj = await _session.scalar(filter)
        else:
            _query = select(func.count()).select_from(
                select(self.model).filter_by(**filter)
            )
            _obj = (await _session.execute(_query)).scalar()
        return _obj


class Model(Base):  # type: ignore
    __abstract__ = True
    __table_args__: Tuple[Any, ...] = ({"extend_existing": True},)

    @property
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def apply(
        cls, session: AsyncSession, redis: Union[Redis, RedisCluster, None]
    ) -> PostgresClient:
        return PostgresClient(cls, session, redis)


class Postgres:
    engine = None

    def __init__(self, url: str, *args, **kwargs) -> None:
        super(Postgres, self).__init__(*args, **kwargs)
        self.Model = Model
        self.url = url

    def connect(self, **kwargs):
        if Postgres.engine is None:
            Postgres.engine = create_async_engine(url=self.url, **kwargs)
            try:
                parsed = urlparse(self.url)
                url_replaced = parsed._replace(
                    netloc="{}:{}@{}:{}".format(
                        parsed.username, "******", parsed.hostname, parsed.port
                    )
                )
                logger.debug(f"Database connected: {url_replaced.geturl()}")
            except Exception:
                logger.debug("Database connected")
        else:
            logger.warning("connection is created")

    async def disconnect(self):
        if self.engine:
            await self.engine.dispose()
            await self.session_scope.close()
            logger.debug("Database disconnected")

    def make_session(self, options: dict = {}, scope=None):
        options.setdefault("class_", AsyncSession)
        options.setdefault("query_cls", Query)
        options.setdefault("expire_on_commit", False)
        session_factory = async_sessionmaker(bind=Postgres.engine, **options)
        self.session = session_factory
        self.session_scope = async_scoped_session(
            session_factory, scopefunc=scope if scope else _current_task
        )()
