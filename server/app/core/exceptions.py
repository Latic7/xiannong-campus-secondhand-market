class BusinessError(Exception):
    def __init__(self, message: str, code: int = 4000, status_code: int = 400, data=None) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.data = data
        super().__init__(message)


class ResourceNotFoundError(BusinessError):
    def __init__(self, message: str = "resource not found", data=None) -> None:
        super().__init__(message=message, code=4040, status_code=404, data=data)


class StateConflictError(BusinessError):
    def __init__(self, message: str = "state conflict", data=None) -> None:
        super().__init__(message=message, code=4090, status_code=409, data=data)


class DuplicateConflictError(BusinessError):
    def __init__(self, message: str = "duplicate operation", data=None) -> None:
        super().__init__(message=message, code=4091, status_code=409, data=data)


class AuthenticationError(BusinessError):
    def __init__(self, message: str = "authentication required", data=None) -> None:
        super().__init__(message=message, code=4010, status_code=401, data=data)


class ForbiddenError(BusinessError):
    def __init__(self, message: str = "forbidden", data=None) -> None:
        super().__init__(message=message, code=4030, status_code=403, data=data)


class InvalidRequestError(BusinessError):
    def __init__(self, message: str = "invalid request", data=None) -> None:
        super().__init__(message=message, code=4000, status_code=400, data=data)
