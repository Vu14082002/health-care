import logging
from typing import Awaitable, Callable, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.exception import BadRequest, BaseException, InternalServer
from src.enum import ErrorCode


def catch_error_repository(message: str | None = None):
    def decorator(func):
        async def _rollback_session(self):
            try:
                logging.info("Rolling back session")
                await self.session.rollback()
            except Exception as rollback_error:
                logging.error(f"Error during rollback: {rollback_error}")

        async def wrapper(self, *args, **kwargs):
            logging.info(
                f"Executing {func.__name__} with args: {args} and kwargs: {kwargs}"
            )
            try:
                result = await func(self, *args, **kwargs)
                logging.info(f"{func.__name__} executed successfully")
                return result
            except IntegrityError as e:
                logging.error(f"Database integrity error in {func.__name__}: {e}")
                await _rollback_session(self)
                raise BadRequest(
                    error_code=ErrorCode.DATABASE_ERROR.name,
                    errors={"message": "Database constraint violation"},
                )
            except SQLAlchemyError as e:
                logging.error(f"SQLAlchemy error in {func.__name__}: {e}")
                await _rollback_session(self)
                raise InternalServer(
                    error_code=ErrorCode.DATABASE_ERROR.name,
                    errors={"message": "Database error occurred"},
                )
            except Exception as e:
                if isinstance(e, BaseException):
                    logging.error(f"Business logic error in {func.__name__}: {e}")
                    await _rollback_session(self)
                    raise e
                logging.error(f"Unexpected error in {func.__name__}: {e}")
                await _rollback_session(self)
                raise InternalServer(
                    error_code=ErrorCode.SERVER_ERROR.name,
                    errors={
                        "message": message
                        or "Server is currently unable to handle this request, please try again later."
                    },
                )

        return wrapper

    return decorator


def catch_error_helper(message: Optional[str] = None):
    def decorator(func: Callable[..., Awaitable]):
        async def wrapper(self, *args, **kwargs):
            logging.info(
                f"Executing {func.__name__} with args: {args} and kwargs: {kwargs}"
            )
            try:
                result = await func(self, *args, **kwargs)
                logging.info(f"{func.__name__} executed successfully")
                return result
            except Exception as e:
                if isinstance(e, BaseException):
                    raise e
                logging.error(f"Unexpected error in {func.__name__}: {e}")
                raise InternalServer(
                    error_code=ErrorCode.SERVER_ERROR.name,
                    errors={
                        "message": message
                        or "Server is currently unable to handle this request, please try again later."
                    },
                )

        return wrapper

    return decorator
