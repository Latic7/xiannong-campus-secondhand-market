from typing import Literal

from pydantic import BaseModel


ReportTargetType = Literal["product", "user", "order"]
AppealTargetType = Literal["report", "user_status"]
ReportStatus = Literal["open", "rejected", "handled"]


class ReportCreateRequest(BaseModel):
	targetType: ReportTargetType
	targetId: int
	reason: str


class AppealCreateRequest(BaseModel):
	targetType: AppealTargetType
	targetId: int
	reason: str


class Report(BaseModel):
	id: int
	reporterId: int | None = None
	targetType: ReportTargetType
	targetId: int
	reason: str
	status: ReportStatus
