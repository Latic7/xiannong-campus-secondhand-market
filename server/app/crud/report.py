from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.report import Report


def _to_schema_dict(report: Report) -> dict:
	"""将 ORM Report 对象转为 API 响应字典，对齐 OpenAPI Report schema。"""
	return {
		"id": report.id,
		"reporterId": report.reporter_id,
		"targetType": report.target_type,
		"targetId": report.target_id,
		"reason": report.reason,
		"status": report.status,
		"createdAt": report.created_at.isoformat() if report.created_at else None,
		"handledAt": report.handled_at.isoformat() if report.handled_at else None,
		"assigneeId": report.assignee_id,
		"handleAction": report.handle_action,
		"handleReason": report.handle_reason,
	}


# 分页查询最大 page_size，防止一次拉取过多数据
_MAX_PAGE_SIZE = 100


def _clamp_size(size: int) -> int:
	"""将 page_size 限制在 [1, _MAX_PAGE_SIZE] 范围内。"""
	return max(1, min(size, _MAX_PAGE_SIZE))


def create_report(record: dict) -> dict:
	with SessionLocal() as db:
		model = Report(
			reporter_id=record.get("reporterId"),
			target_type=record["targetType"],
			target_id=record["targetId"],
			reason=record["reason"],
			status=record.get("status", "OPEN"),
		)
		db.add(model)
		db.commit()
		db.refresh(model)
		return _to_schema_dict(model)


def get_report(report_id: int) -> dict | None:
	with SessionLocal() as db:
		report = db.get(Report, report_id)
		if report is None:
			return None
		return _to_schema_dict(report)


def list_reports(
	page: int = 1,
	size: int = 20,
	status: str | None = None,
	target_type: str | None = None,
) -> tuple[list[dict], int]:
	"""分页查询举报列表，支持按 status 和 target_type 筛选。"""
	size = _clamp_size(size)
	with SessionLocal() as db:
		filters = []
		if status:
			filters.append(Report.status == status)
		if target_type:
			filters.append(Report.target_type == target_type)

		total = db.scalar(
			select(func.count(Report.id)).where(*filters) if filters else select(func.count(Report.id))
		) or 0

		stmt = (
			select(Report)
			.order_by(Report.created_at.desc(), Report.id.desc())
			.offset((page - 1) * size)
			.limit(size)
		)
		if filters:
			stmt = stmt.where(*filters)

		rows = db.scalars(stmt).all()
		return ([_to_schema_dict(row) for row in rows], int(total))


def update_report(report_id: int, updates: dict) -> dict | None:
	with SessionLocal() as db:
		report = db.get(Report, report_id)
		if report is None:
			return None

		if "status" in updates:
			report.status = updates["status"]
		if "action" in updates:
			report.handle_action = updates["action"]
		if "reason" in updates:
			report.handle_reason = updates["reason"]
		if "assigneeId" in updates:
			report.assignee_id = updates["assigneeId"]

		report.handled_at = datetime.now(timezone.utc)
		db.commit()
		db.refresh(report)
		return _to_schema_dict(report)
