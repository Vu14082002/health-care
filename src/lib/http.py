# -*- coding: utf-8 -*-
from functools import wraps
import httpx
import aiohttp


def process(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        args = list(args)
        _url = ""
        if len(args) > 1:
            _url = args[1]
        else:
            _url = kwargs.get("url", "")
            args.append("")
            del kwargs["url"]
        if _url.startswith("/"):
            _url = _url[1:]
        args[1] = _url
        _result = await func(*args, **kwargs)
        return _result

    return wrapper


class AsyncHttpClient:
    def __init__(self, base_url: str, headers={}) -> None:
        timeout = httpx.Timeout(20.0, connect=60.0)
        limits = httpx.Limits(max_keepalive_connections=40, max_connections=500)
        self.client = httpx.AsyncClient(timeout=timeout, limits=limits, verify=False)
        if not base_url.endswith("/"):
            base_url = base_url + "/"
        self.base_url = httpx.URL(base_url)

        self.headers = {"content-type": "application/json"}
        if headers:
            self.headers = headers

    @process
    async def get(self, url, params={}, headers={}, *args, **kwargs) -> httpx.Response:
        timeout = httpx.Timeout(20.0, connect=60.0)
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=500)
        async with httpx.AsyncClient(
            timeout=timeout, limits=limits, verify=False
        ) as client:
            _response = await client.get(
                self.base_url.join(url),
                params=params,
                headers=headers if headers else self.headers,
                *args,
                **kwargs,
            )
        return _response

    @process
    async def post(self, url, data={}, headers={}, *args, **kwargs) -> httpx.Response:
        timeout = httpx.Timeout(20.0, connect=60.0)
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=500)
        async with httpx.AsyncClient(
            timeout=timeout, limits=limits, verify=False
        ) as client:
            _response = await client.post(
                self.base_url.join(url),
                json=data,
                headers=headers if headers else self.headers,
                *args,
                **kwargs,
            )
        return _response

    @process
    async def put(self, url, data={}, headers={}, *args, **kwargs) -> httpx.Response:
        timeout = httpx.Timeout(20.0, connect=60.0)
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=500)
        async with httpx.AsyncClient(
            timeout=timeout, limits=limits, verify=False
        ) as client:
            _response = await client.put(
                self.base_url.join(url),
                json=data,
                headers=headers if headers else self.headers,
                *args,
                **kwargs,
            )
        return _response

    @process
    async def delete(self, url, data={}, headers={}, *args, **kwargs) -> httpx.Response:
        timeout = httpx.Timeout(20.0, connect=60.0)
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=500)
        async with httpx.AsyncClient(
            timeout=timeout, limits=limits, verify=False
        ) as client:
            _response = await client.request(
                "DELETE",
                self.base_url.join(url),
                json=data,
                headers=headers if headers else self.headers,
                *args,
                **kwargs,
            )

        return _response


class AioHttpClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.headers = {"Content-type": "application/json"}

    async def get(
        self, url, params={}, headers={}, *args, **kwargs
    ) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            _response = await session.get(
                url=f"{self.base_url}/{url}",
                params=params,
                headers=headers if headers else self.headers,
                *args,
                **kwargs,
            )
            return _response

    async def post(
        self, url, data={}, headers={}, *args, **kwargs
    ) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            _response = await session.post(
                url=f"{self.base_url}/{url}",
                json=data,
                headers=headers if headers else self.headers,
                *args,
                **kwargs,
            )
            return _response

    async def put(
        self, url, data={}, headers={}, *args, **kwargs
    ) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            _response = await session.put(
                url=f"{self.base_url}/{url}",
                json=data,
                headers=headers if headers else self.headers,
                *args,
                **kwargs,
            )
            return _response

    async def delete(
        self, url, data={}, headers={}, *args, **kwargs
    ) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            _response = await session.request(
                "DELETE",
                f"{self.base_url}/{url}",
                json=data,
                headers=headers if headers else self.headers,
                *args,
                **kwargs,
            )
            return _response
