from typing import Literal

from pydantic import BaseModel


UserStatus = Literal["active", "banned"]
ReportAction = Literal["reject", "warning", "unlist_product", "ban_user"]


class UserStatusPatchRequest(BaseModel):
	status: UserStatus
	reason: str | None = None


class ProductReviewRequest(BaseModel):
	result: str
	reason: str | None = None


class ReportHandleRequest(BaseModel):
	action: ReportAction
	reason: str | None = None
