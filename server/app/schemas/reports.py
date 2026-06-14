from datetime import datetime
from typing import Literal

from pydantic import BaseModel


ReportTargetType = Literal["PRODUCT", "USER", "ORDER"]
AppealTargetType = Literal["report", "user_status"]
ReportStatus = Literal["OPEN", "REJECTED", "HANDLED"]


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
	createdAt: datetime | None = None
	handledAt: datetime | None = None
	assigneeId: int | None = None
	handleAction: str | None = None
	handleReason: str | None = None
