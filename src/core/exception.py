from src.enum import ErrorCode


class BaseException(Exception):
    def __init__(self, msg="", *args: object) -> None:
        super().__init__(*args)
        self.msg = msg
        self.status = 400
        self.errors = {}
        self.error_code = ErrorCode.UNKNOWN_ERROR.name


class BadRequest(BaseException):
    def __init__(
        self,
        msg="Bad request",
        errors={},
        error_code=ErrorCode.BAD_REQUEST.name,
        *args: object
    ) -> None:
        super().__init__(msg, *args)
        self.errors = errors
        self.error_code = error_code


class Forbidden(BaseException):
    def __init__(
        self,
        msg="Forbidden",
        errors={},
        error_code=ErrorCode.FORBIDDEN.name,
        *args: object
    ) -> None:
        super().__init__(msg, *args)
        self.errors = errors
        self.status = 403
        self.error_code = error_code


class NotFound(BaseException):
    def __init__(
        self,
        msg="NotFound",
        errors={},
        error_code=ErrorCode.NOT_FOUND.name,
        *args: object
    ) -> None:
        super().__init__(msg, *args)
        self.errors = errors
        self.status = 404
        self.error_code = error_code


class MethodNotAllow(BaseException):
    def __init__(
        self,
        msg="Method not allow",
        error_code=ErrorCode.METHOD_NOT_ALLOW.name,
        *args: object
    ) -> None:
        super().__init__(msg, *args)
        self.status = 405
        self.error_code = error_code


class ConflictError(BaseException):
    def __init__(
        self,
        msg="Conflict",
        errors={},
        error_code=ErrorCode.CONFLICT.name,
        *args: object
    ) -> None:
        super().__init__(msg, *args)
        self.errors = errors
        self.status = 409
        self.error_code = error_code


class InternalServer(BaseException):
    def __init__(
        self,
        msg="Internal server error",
        errors={},
        error_code=ErrorCode.SERVER_ERROR.name,
        *args: object
    ) -> None:
        super().__init__(msg, *args)
        self.errors = errors
        self.status = 500
        self.error_code = error_code


class Unauthorized(BaseException):
    def __init__(
        self,
        msg="Unauthorized",
        errors={},
        error_code=ErrorCode.UNAUTHORIZED.name,
        *args: object
    ) -> None:
        super().__init__(msg, *args)
        self.errors = errors
        self.status = 401
        self.error_code = error_code


class SignatureVerifyFail(BaseException):
    def __init__(
        self,
        msg="Signature verify fail",
        errors={},
        error_code=ErrorCode.SIGNATURE_VERIFY_FAIL.name,
        *args: object
    ) -> None:
        super().__init__(msg, *args)
        self.errors = errors
        self.status = 409
        self.error_code = error_code
