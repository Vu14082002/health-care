import contextlib
import json
import logging

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.schemas import SchemaGenerator

from src.apis import routes
from src.config import config
from src.core import sentry
from src.core.cache import Cache, CustomKeyMaker, RedisBackend
from src.core.logger import DefaultFormatter, logger
from src.core.middlewares.header import HeadersMiddleware
from src.core.middlewares.sqlalchemy import SQLAlchemyMiddleware
from src.enum import ErrorCode
from src.factory import Factory
from src.swagger import SwaggerUI

schemas = SchemaGenerator(
    {
        "openapi": "3.0.0",
        "info": {"title": "Health Care", "version": "1.0"},
        # "servers": [{"url": "/" if config.ENV == "DEV" else config.PREFIX_URL}],
        "servers": [{"url": "/"}, {"url": "/" if config.ENV == "DEV" else config.PREFIX_URL}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
    }
)


class Application(Starlette):
    """_summary_

    Args:
        Starlette (_type_): _description_
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        async def exc_method_not_allow(request: Request, exc: HTTPException):
            return Response(
                content=json.dumps(
                    {
                        "data": "",
                        "msg": "Method not allow",
                        "error": {},
                        "error_code": ErrorCode.METHOD_NOT_ALLOW.name,
                    }
                ),
                status_code=405,
                headers={"Content-type": "application/json"},
            )

        async def exc_not_found(request: Request, exc: HTTPException):
            return Response(
                content=json.dumps(
                    {
                        "data": "",
                        "msg": "Not found",
                        "error": {},
                        "error_code": ErrorCode.NOT_FOUND.name,
                    }
                ),
                status_code=404,
                headers={"Content-type": "application/json"},
            )

        async def exc_internal_server(request: Request, exc: HTTPException):
            return Response(
                content=json.dumps(
                    {
                        "data": "",
                        "msg": "Internal server error",
                        "error": {},
                        "error_code": ErrorCode.SERVER_ERROR.name,
                    }
                ),
                status_code=500,
                headers={"Content-type": "application/json"},
            )

        _excs = self.exception_handlers
        self.exception_handlers = {
            **_excs,
            405: exc_method_not_allow,
            404: exc_not_found,
            500: exc_internal_server,
        }


def config_app_logger():
    logger = logging.getLogger("uvicorn.access")
    logger.setLevel(logging.DEBUG)
    formatter = DefaultFormatter(
        fmt="%(levelprefix)s %(asctime)s [%(process)s] [%(filename)s:%(lineno)d] %(message)s",
        use_colors=True,
        datefmt="%d-%m-%Y %H:%M:%S",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@contextlib.asynccontextmanager
async def lifespan(app):
    logger.debug("Server start with environment: %s", config.ENV)
    config_app_logger()
    Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())

    sentry.setup(config.SENTRY_DSN)

    # create a default admin account
    # admin_helper = await Factory().get_admin_helper()
    # await admin_helper.create_admin()

    yield {}


def openapi_schema(request):
    return schemas.OpenAPIResponse(request=request)


routes.append(Route("/schema", endpoint=openapi_schema,
              include_in_schema=False))
app = Application(
    routes=routes,
    lifespan=lifespan,
    middleware=[
        Middleware(SQLAlchemyMiddleware),
        Middleware(HeadersMiddleware),
        Middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )
    ]
)
SwaggerUI(
    app,
    url="/docs",
    css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
)
