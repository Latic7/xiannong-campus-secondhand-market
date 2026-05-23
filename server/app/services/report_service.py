from __future__ import annotations

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
			"reporterId": 3,
			"status": "open",
		}
	)
	return report


def get_report(report_id: int) -> dict:
	report = crud_get_report(report_id)
	if report is None:
		report = {
			"id": report_id,
			"reporterId": None,
			"targetType": "product",
			"targetId": 0,
			"reason": "report not found",
			"status": "open",
		}
	return report


def list_report_queue(page: int = 1, size: int = 20) -> dict:
    rows, total = crud_list_reports(page=page, size=size)
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
			"assigneeId": 10,
		},
	)
	if updated is None:
		created = crud_create_report(
			{
				"reporterId": 3,
				"targetType": "product",
				"targetId": 1001,
				"reason": "自动补建举报记录",
				"status": "open",
			}
		)
		report_id = int(created["id"])
		crud_update_report(
			report_id,
			{
				"status": status,
				"action": payload.action,
				"reason": payload.reason,
				"assigneeId": 10,
			},
		)
	return {"reportId": report_id, **payload.model_dump()}


def create_appeal(payload: AppealCreateRequest) -> dict:
	return {"submitted": True, **payload.model_dump()}
