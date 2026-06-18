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

class UnauthorizedError(BusinessError):
    """未认证异常(401)- 未登录或 token 无效"""
    def __init__(self, message: str = "unauthorized", data=None) -> None:
        super().__init__(message=message, code=10030, status_code=401, data=data)


class PermissionDeniedError(BusinessError):
    """权限拒绝异常(403)- 已登录但权限不足"""
    def __init__(self, message: str = "permission denied", data=None) -> None:
        super().__init__(message=message, code=10060, status_code=403, data=data)


class TokenInvalidError(UnauthorizedError):
    """Token 无效异常"""
    def __init__(self, message: str = "access token invalid", data=None) -> None:
        super().__init__(message=message, data=data)