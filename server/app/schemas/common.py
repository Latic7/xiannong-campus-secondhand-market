from pydantic import BaseModel, Field

# Re-export validated schemas from dedicated modules (single source of truth)
from app.schemas.orders import OrderCreateRequest, OrderReviewRequest  # noqa: F401
from app.schemas.products import ProductCreateRequest, ProductUpdateRequest  # noqa: F401
from app.schemas.reports import AppealCreateRequest, ReportCreateRequest  # noqa: F401


class WxLoginRequest(BaseModel):
    code: str
    clientId: str | None = None
    admin_secret: str | None = Field(None, description="管理员创建密码（可选）")


class TokenRefreshRequest(BaseModel):
    refreshToken: str


class UserProfileUpdateRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None
    college: str | None = None
    contact: str | None = None