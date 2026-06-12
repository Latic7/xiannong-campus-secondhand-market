from __future__ import annotations

from app.core.exceptions import ResourceNotFoundError
from app.crud.report import create_report as crud_create_report
from app.crud.report import get_report as crud_get_report
from app.crud.report import list_reports as crud_list_reports
from app.crud.report import update_report as crud_update_report
from app.schemas.admin import ReportHandleRequest
from app.schemas.reports import AppealCreateRequest, ReportCreateRequest


def create_report(payload: ReportCreateRequest) -> dict:
	report = crud_create_report(
		{
			**payload.model_dump(),
			"reporterId": 3,  # TODO: 接入登录态后替换为当前用户 ID
			"status": "open",
		}
	)
	return report


def get_report(report_id: int) -> dict:
	report = crud_get_report(report_id)
	if report is None:
		raise ResourceNotFoundError(f"举报记录 {report_id} 不存在")
	return report


def list_report_queue(page: int = 1, size: int = 20, status: str | None = None, target_type: str | None = None) -> dict:
	rows, total = crud_list_reports(page=page, size=size, status=status, target_type=target_type)
	return {
		"list": rows,
		"page": {"page": page, "size": size, "total": total},
	}


def handle_report(report_id: int, payload: ReportHandleRequest) -> dict:
	status = "rejected" if payload.action == "reject" else "handled"
	updated = crud_update_report(
		report_id,
		{
			"status": status,
			"action": payload.action,
			"reason": payload.reason,
			"assigneeId": 10,  # TODO: 接入登录态后替换为当前管理员 ID
		},
	)
	if updated is None:
		raise ResourceNotFoundError(f"举报记录 {report_id} 不存在，无法处理")

	return {"reportId": report_id, **payload.model_dump()}


def create_appeal(payload: AppealCreateRequest) -> dict:
	return {"submitted": True, **payload.model_dump()}
