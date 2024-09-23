import logging
from typing import Awaitable, Callable
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.enum import ErrorCode


def catch_error_repository(func: Callable[..., Awaitable]):  # type: ignore

    async def _rollback_session(self):
        try:
            logging.info("Rolling back session")
            await self.session.rollback()
        except Exception as rollback_error:
            logging.error(f"Error during rollback: {rollback_error}")

    async def wrapper(self, *args, **kwargs):
        logging.info(f"Executing {func.__name__} with args: {args} and kwargs: {kwargs}")
        try:
            result = await func(self, *args, **kwargs)
            logging.info(f"{func.__name__} executed successfully")
            return result
        except (BadRequest, Forbidden, InternalServer) as e:
            logging.error(f"Business logic error in {func.__name__}: {e}")
            await _rollback_session(self)  # Gọi trực tiếp _rollback_session
            raise e
        except IntegrityError as e:
            logging.error(f"Database integrity error in {func.__name__}: {e}")
            await _rollback_session(self)  # Gọi trực tiếp _rollback_session
            raise BadRequest(
                error_code=ErrorCode.DATABASE_ERROR.name,
                errors={"message": "Database constraint violation"},
            )
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemy error in {func.__name__}: {e}")
            await _rollback_session(self)  # Gọi trực tiếp _rollback_session
            raise InternalServer(
                error_code=ErrorCode.DATABASE_ERROR.name,
                errors={"message": "Database error occurred"},
            )
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            await _rollback_session(self)  # Gọi trực tiếp _rollback_session
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server is currently unable to handle this request, please try again later."
                },
            )

    return wrapper
