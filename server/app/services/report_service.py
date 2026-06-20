from __future__ import annotations

from sqlalchemy.orm import Session

from app.api.deps.auth import CurrentActor
from app.core.exceptions import ResourceNotFoundError
from app.crud.report import create_report as crud_create_report
from app.crud.report import get_report as crud_get_report
from app.crud.report import list_reports_with_target as crud_list_reports_with_target
from app.crud.report import update_report as crud_update_report
from app.schemas.admin import ReportHandleRequest
from app.schemas.reports import AppealCreateRequest, ReportCreateRequest


def create_report(payload: ReportCreateRequest, actor: CurrentActor | None = None) -> dict:
    reporter_id = actor.user_id if actor else 3
    report = crud_create_report(
        {
            **payload.model_dump(),
            "reporterId": reporter_id,
            "status": "OPEN",
        }
    )
    return report


def get_report(report_id: int) -> dict:
    report = crud_get_report(report_id)
    if report is None:
        raise ResourceNotFoundError(f"举报记录 {report_id} 不存在")
    return report


def list_report_queue(
	db: Session,
	page: int = 1,
	size: int = 20,
	status: str | None = None,
	target_type: str | None = None,
) -> dict:
	rows, total = crud_list_reports_with_target(
		db,
		page=page,
		size=size,
		status=status,
		target_type=target_type,
	)
	return {
		"list": rows,
		"page": {"page": page, "size": size, "total": total},
	}


def list_my_reports(
    db: Session,
    actor: CurrentActor,
    page: int = 1,
    size: int = 20,
    status: str | None = None,
    target_type: str | None = None,
) -> dict:
    # 与举报队列一致，附带被举报对象摘要，供前端富卡片展示
    rows, total = crud_list_reports_with_target(
        db,
        page=page,
        size=size,
        status=status,
        target_type=target_type,
        reporter_id=actor.user_id,
    )
    return {
        "list": rows,
        "page": {"page": page, "size": size, "total": total},
        "filters": {"status": status, "targetType": target_type},
    }


def handle_report(report_id: int, payload: ReportHandleRequest, actor: CurrentActor | None = None) -> dict:
    status = "REJECTED" if payload.action == "reject" else "HANDLED"
    assignee_id = actor.user_id if actor else 10
    updated = crud_update_report(
        report_id,
        {
            "status": status,
            "action": payload.action,
            "reason": payload.reason,
            "assigneeId": assignee_id,
        },
    )
    if updated is None:
        raise ResourceNotFoundError(f"举报记录 {report_id} 不存在，无法处理")

    return {"reportId": report_id, **payload.model_dump()}


def create_appeal(payload: AppealCreateRequest) -> dict:
    return {"submitted": True, **payload.model_dump()}
