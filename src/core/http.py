from functools import wraps
import httpx
import aiohttp


def process(func):
    """
     Decorator to process url. This is useful for functions that need to be async. The function is called with the url as first argument and the rest of the arguments are passed to the function
     
     @param func - The function to be decorated
     
     @return The result of the function that is passed to the function as first argument and the rest of the arguments are
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        """
         Wrapper to add url to args and return result. It is used as a context manager for async functions.
         
         
         @return result of async function with url added to args and return it as a result of async function with url
        """
        args = list(args)
        _url: str = ""
        # Set the url to the url.
        if len(args) > 1:
            _url = args[1]
        else:
            _url = kwargs.get("url", "")
            args.append("")
            del kwargs["url"]
        # Get the URL from the URL.
        if _url.startswith("/"):
            _url = _url[1:]
        args[1] = _url
        _result = await func(*args, **kwargs)
        return _result

    return wrapper


class AsyncHttpClient:
    def __init__(self, base_url: str, headers={}) -> None:
        """
         Initialize AsyncClient with default parameters. This is the method that must be called before any other methods.
         
         @param base_url - The base URL to use for the API
         @param headers - A dictionary of headers to send with the API
         
         @return A reference to the
        """
        timeout = httpx.Timeout(20.0, connect=60.0)
        limits = httpx.Limits(max_keepalive_connections=40, max_connections=500)
        self.client = httpx.AsyncClient(timeout=timeout, limits=limits, verify=False)
        # Add a slash to base_url if it doesn t end with a slash
        if not base_url.endswith("/"):
            base_url = base_url + "/"
        self.base_url = httpx.URL(base_url)

        self.headers = {"content-type": "application/json"}
        # Set headers to be used for the request.
        if headers:
            self.headers = headers

    @process
    async def get(self, url, params={}, headers={}, *args, **kwargs) -> httpx.Response:
        """
         Make a GET request to the URL. This is a wrapper around : meth : ` requests. Session. get ` with timeout and keep alive connections
         
         @param url - The URL to make the request to
         @param params - A dictionary of key value pairs to send with the request
         @param headers - A dictionary of key value pairs to send with the request
         
         @return A : class : ` Response ` object that can be used to inspect the response and raise an exception if there is
        """
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
                **kwargs
            )
        return _response

    @process
    async def post(self, url, data={}, headers={}, *args, **kwargs) -> httpx.Response:
        """
         Send a POST request to the API. This is a coroutine. If you need to wait for the response use
         
         @param url - The URL to send the request to.
         @param data - The data to send in the body of the request.
         @param headers - The headers to send in the request. Defaults to {}.
         
         @return The response from the API call as a : class : ` Response ` object. note :: The timeout and connection limits are hardwired to 20. 0 seconds
        """
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
                **kwargs
            )
        return _response

    @process
    async def put(self, url, data={}, headers={}, *args, **kwargs) -> httpx.Response:
        """
         Send a PUT request to the API. This is a coroutine. If you want to wait for the response use
         
         @param url - The URL to send the request to.
         @param data - The data to send in the body of the request.
         @param headers - The headers to send in the request. Defaults to {}.
         
         @return The response from the API call as a : class : ` Response ` object. code - block ::
        """
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
                **kwargs
            )
        return _response

    @process
    async def delete(self, url, data={}, headers={}, *args, **kwargs) -> httpx.Response:
        """
         Send a DELETE request to the API. This is a coroutine. If you don't want a response use
         
         @param url - The URL to send the request to.
         @param data - The data to send in the request. Defaults to {}.
         @param headers - The headers to send in the request. Defaults to {}.
         
         @return The response from the API as a : class : ` Response ` object. >>> client = await client. get ('test')
        """
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
                **kwargs
            )

        return _response
