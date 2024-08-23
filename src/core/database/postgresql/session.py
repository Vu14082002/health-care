from contextlib import asynccontextmanager
from contextvars import ContextVar, Token
from typing import Union

from sqlalchemy.ext.asyncio import (AsyncSession, async_scoped_session,
                                    create_async_engine)
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.sql.expression import Delete, Insert, Update

from src.config import config

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    """
     Get the current session context. This is useful for debugging and to ensure that we don't accidentally get a value that's in the session for the first time.


     @return The current session context or None if there is none in the session. Note that it may be different from the value returned by : func : ` get_session
    """
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    """
     Set the session context. This is a convenience method for calling : func : ` set_session_context ` with the given session id.

     @param session_id - The session id to set. It must be a string and not None.

     @return The token that was set or None if no context was set for the session id. Note that this will be a Token but not a Session
    """
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    """
     Reset the session context. This is a no - op if there is no session context to reset.

     @param context - The context to reset. It must be a : class : ` telegram. Session ` instance.

     @return None. note :: This function does not return anything. Use : func : ` get_or_create
    """
    session_context.reset(context)


engines = {
    "writer": create_async_engine(config.POSTGRES_URL_MASTER, pool_recycle=3600),
    "reader": create_async_engine(config.POSTGRES_URL_SLAVE, pool_recycle=3600),
}


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kwargs):
        """
         Return the : class : `. SyncEngine ` to use for this query. This is a no - op if flushing is enabled.

         @param mapper - The : class : `. Mapper ` that is executing the query.
         @param clause - The clause that is executing. It can be a SQLAlchemy clause or an instance of : class : `. ClauseElement `.

         @return A : class : `. SyncEngine ` that is used to write to and read from the database
        """
        # Returns the engine for flushing the current statement.
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
     Get the database session. This can be used for dependency injection. Yields session_scope : SQLAlchemy scope
    """
    """
    Get the database session.
    This can be used for dependency injection.

    :return: The database session.
    """
    try:
        yield session_scope
    finally:
        await session_scope.close()
