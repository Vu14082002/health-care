from enum import Enum
from functools import wraps
import traceback

from src.core.database.postgresql import session_scope


class Propagation(Enum):
    REQUIRED = "required"
    REQUIRED_NEW = "required_new"


class Transactional:
    def __init__(self, propagation: Propagation = Propagation.REQUIRED):
        self.propagation = propagation

    def __call__(self, function):
        """
        The function is a decorator that handles transaction propagation in Python asyncio functions.
        
        :param function: The `function` parameter in the code snippet represents the function that is being
        decorated by the `__call__` method. This function will be executed within the `decorator` function,
        which is a wrapper function created by the `__call__` method. The `function` parameter is passed
        :return: The `__call__` method is returning a decorator function that wraps the input `function`.
        This decorator function is an asynchronous function that first checks the `propagation` attribute of
        the class instance and then calls different internal methods based on the value of `propagation`. If
        an exception occurs during the execution of the `function`, the decorator will print the traceback,
        rollback the session, and then re
        """
        @wraps(function)
        async def decorator(*args, **kwargs):
            try:
                if self.propagation == Propagation.REQUIRED:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                elif self.propagation == Propagation.REQUIRED_NEW:
                    result = await self._run_required_new(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
                else:
                    result = await self._run_required(
                        function=function,
                        args=args,
                        kwargs=kwargs,
                    )
            except Exception as exception:
                traceback.print_exc()
                await session_scope.rollback()
                raise exception

            return result

        return decorator

    async def _run_required(self, function, args, kwargs) -> None:
        """
        Run a required transaction.

        :param function: The function to be executed within the transaction.
        :param args: The positional arguments to be passed to the function.
        :param kwargs: The keyword arguments to be passed to the function.
        :return: The result of the function execution.
        """
        result = await function(*args, **kwargs)
        await session_scope.commit()
        return result

    async def _run_required_new(self, function, args, kwargs) -> None:
        """
        Run a new required transaction.

        :param function: The function to be executed within the transaction.
        :param args: The positional arguments to be passed to the function.
        :param kwargs: The keyword arguments to be passed to the function.
        :return: The result of the function execution.
        """
        session_scope.begin()
        result = await function(*args, **kwargs)
        await session_scope.commit()
        return result
