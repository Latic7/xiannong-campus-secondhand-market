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
