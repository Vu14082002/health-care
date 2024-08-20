from contextlib import asynccontextmanager
from contextvars import ContextVar, Token
from typing import Union

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.sql.expression import Delete, Insert, Update

from src.config import config

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


engines = {
    "writer": create_async_engine(config.POSTGRES_URL_MASTER, pool_recycle=3600),
    "reader": create_async_engine(config.POSTGRES_URL_SLAVE, pool_recycle=3600),
}


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kwargs):
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):
            return engines["writer"].sync_engine
        return engines["reader"].sync_engine


async_session_factory = sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
    expire_on_commit=False,
)

session_scope: Union[AsyncSession, async_scoped_session] = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context,
)


@asynccontextmanager
async def get_session():
    """
    Get the database session.
    This can be used for dependency injection.

    :return: The database session.
    """
    try:
        yield session_scope
    finally:
        await session_scope.close()
