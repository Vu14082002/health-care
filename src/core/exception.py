from src.enum import ErrorCode


class BaseException(Exception):
    def __init__(self, *args: object, msg="") -> None:
        super().__init__(*args)
        self.msg = msg
        self.status = 400
        self.errors = {}
        self.error_code = ErrorCode.UNKNOWN_ERROR.name


class BadRequest(BaseException):
    def __init__(
        self,
        *args: object,
        msg="Bad request",
        errors=None,
        error_code=ErrorCode.BAD_REQUEST.name,
    ) -> None:
        super().__init__(msg, *args)
        self.errors = {} if errors is None else errors
        self.error_code = error_code


class Forbidden(BaseException):
    def __init__(
        self,
        *args: object,
        msg="Forbidden",
        errors=None,
        error_code=ErrorCode.FORBIDDEN.name,
    ) -> None:
        super().__init__(msg, *args)
        self.errors = {} if errors is None else errors
        self.status = 403
        self.error_code = error_code


class NotFound(BaseException):
    def __init__(
        self,
        *args: object,
        msg="NotFound",
        errors=None,
        error_code=ErrorCode.NOT_FOUND.name,
    ) -> None:
        super().__init__(msg, *args)
        self.errors = {} if errors is None else errors
        self.status = 404
        self.error_code = error_code


class MethodNotAllow(BaseException):
    def __init__(
        self,
        *args: object,
        msg="Method not allow",
        error_code=ErrorCode.METHOD_NOT_ALLOW.name,
    ) -> None:
        super().__init__(msg, *args)
        self.status = 405
        self.error_code = error_code


class ConflictError(BaseException):
    def __init__(
        self,
        *args: object,
        msg="Conflict",
        errors=None,
        error_code=ErrorCode.CONFLICT.name,

    ) -> None:
        super().__init__(msg, *args)
        self.errors = {} if errors is None else errors
        self.status = 409
        self.error_code = error_code


class InternalServer(BaseException):
    def __init__(
        self,
        *args: object,
        msg="Internal server error",
        errors=None,
        error_code=ErrorCode.SERVER_ERROR.name,
    ) -> None:
        super().__init__(msg, *args)
        self.errors = {} if errors is None else errors
        self.status = 500
        self.error_code = error_code


class Unauthorized(BaseException):
    def __init__(
        self,
        *args: object,
        msg="Unauthorized",
        errors=None,
        error_code=ErrorCode.UNAUTHORIZED.name,
    ) -> None:
        super().__init__(msg, *args)
        self.errors = {} if errors is None else errors
        self.status = 401
        self.error_code = error_code


class SignatureVerifyFail(BaseException):
    def __init__(
        self,
        *args: object,
        msg="Signature verify fail",
        errors=None,
        error_code=ErrorCode.SIGNATURE_VERIFY_FAIL.name,
    ) -> None:
        super().__init__(msg, *args)
        self.errors = {} if errors is None else errors
        self.status = 409
        self.error_code = error_code
