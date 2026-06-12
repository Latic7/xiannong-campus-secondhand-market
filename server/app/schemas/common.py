from pydantic import BaseModel, Field

from app.schemas.orders import OrderCreateRequest, OrderReviewRequest
from app.schemas.products import ProductCreateRequest, ProductUpdateRequest

from app.core.status import ProductStatus, ReportTargetType, UserStatus


class WxLoginRequest(BaseModel):
    code: str
    clientId: str | None = None
    admin_secret: str | None = Field(None, description="管理员创建密码（可选）")  # 只添加这一行


class TokenRefreshRequest(BaseModel):
    refreshToken: str


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None
    college: str | None = None
    contact: str | None = None


class ProductCreateRequest(BaseModel):
    title: str
    price: float
    categoryId: int
    description: str | None = None
    images: list[str] = Field(default_factory=list)


class ProductUpdateRequest(BaseModel):
    title: str | None = None
    price: float | None = None
    categoryId: int | None = None
    description: str | None = None
    status: ProductStatus | None = None


class OrderCreateRequest(BaseModel):
    productId: int
    remark: str | None = None


class OrderReviewRequest(BaseModel):
    score: int
    content: str


class ReportCreateRequest(BaseModel):
    targetType: ReportTargetType
    targetId: int
    reason: str


class AppealCreateRequest(BaseModel):
    targetType: str
    targetId: int
    reason: str


class UserStatusPatchRequest(BaseModel):
    status: UserStatus
    reason: str | None = None


class ProductReviewRequest(BaseModel):
    result: str
    reason: str | None = None


class ReportHandleRequest(BaseModel):
    action: str
    reason: str | None = None