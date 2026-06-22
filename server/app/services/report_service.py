from __future__ import annotations

from sqlalchemy.orm import Session

from app.api.deps.auth import CurrentActor
from app.core.exceptions import ResourceNotFoundError
from app.crud.report import create_report as crud_create_report
from app.crud.report import get_report as crud_get_report
from app.crud.report import list_reports_with_target as crud_list_reports_with_target
from app.crud.report import update_report as crud_update_report
from app.models.product import Product
from app.models.user import User
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
    from app.core.database import SessionLocal
    from app.models.user import User

    status = "REJECTED" if payload.action == "reject" else "HANDLED"
    assignee_id = actor.user_id if actor else 10

    # 获取举报记录，找出被举报人并扣除信誉分
    report = crud_get_report(report_id)
    if report is None:
        raise ResourceNotFoundError(f"举报记录 {report_id} 不存在，无法处理")

    with SessionLocal() as db:
        # 根据举报类型找出目标用户
        target_user_id = None
        if report["targetType"] == "USER":
            target_user_id = report["targetId"]
        elif report["targetType"] == "PRODUCT":
            product = db.get(Product, report["targetId"])
            if product:
                target_user_id = product.owner_id

        # 如果处理动作不是驳回，扣除被举报人信誉分
        if payload.action != "reject" and target_user_id:
            user = db.get(User, target_user_id)
            if user:
                deduction = {"warning": 10, "ban_user": 30, "unlist_product": 5}.get(payload.action, 10)
                user.score = max(0, (user.score or 100) - deduction)
                db.commit()

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


def list_reports_against_user(
    db: Session,
    actor: CurrentActor,
    page: int = 1,
    size: int = 20,
) -> dict:
    """查询针对当前用户的举报（通过被举报对象关联）"""
    from app.models.report import Report as ReportModel
    from sqlalchemy import or_

    rows, total = crud_list_reports_with_target(
        db,
        page=page,
        size=size,
        # 查询 target 是当前用户，或 target 的商品属于当前用户
        target_user_id=actor.user_id,
    )
    return {
        "list": rows,
        "page": {"page": page, "size": size, "total": total},
    }


def create_appeal(payload: AppealCreateRequest) -> dict:
    return {"submitted": True, **payload.model_dump()}
