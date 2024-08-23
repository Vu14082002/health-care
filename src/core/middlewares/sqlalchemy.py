from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send
from src.core.database.postgresql import (
    reset_session_context,
    session_scope,
    set_session_context,
)


class SQLAlchemyMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        """
         Initialize the instance. This is called by the : class : ` ASGIApp ` to allow the object to be used as a context manager

         @param app - The application that will be used for this context manager

         @return A reference to the application to be used as a context manager or ` ` None ` ` if no
        """
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
         The object to send messages to. This can be used to specify a different scope for different request / response calls

         @param scope - The scope of the request. This can be used to specify a different scope for different request / response calls
         @param receive - The object to receive messages from
         @param send
        """
        session_id = str(uuid4())
        context = set_session_context(session_id=session_id)

        try:
            await self.app(scope, receive, send)
        except Exception as exception:
            raise exception
        finally:
            await session_scope.remove()
            reset_session_context(context=context)
