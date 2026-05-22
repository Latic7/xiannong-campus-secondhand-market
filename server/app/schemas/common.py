from pydantic import BaseModel

from app.schemas.orders import OrderCreateRequest, OrderReviewRequest
from app.schemas.products import ProductCreateRequest, ProductUpdateRequest


class WxLoginRequest(BaseModel):
    code: str
    clientId: str | None = None


class TokenRefreshRequest(BaseModel):
    refreshToken: str


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None
    college: str | None = None
    contact: str | None = None


class ReportCreateRequest(BaseModel):
    targetType: str
    targetId: int
    reason: str


class AppealCreateRequest(BaseModel):
    targetType: str
    targetId: int
    reason: str


class UserStatusPatchRequest(BaseModel):
    status: str
    reason: str | None = None


class ProductReviewRequest(BaseModel):
    result: str
    reason: str | None = None


class ReportHandleRequest(BaseModel):
    action: str
    reason: str | None = None
