from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.report import Report


def _to_schema_dict(report: Report) -> dict:
	return {
		"id": report.id,
		"reporterId": report.reporter_id,
		"targetType": report.target_type,
		"targetId": report.target_id,
		"reason": report.reason,
		"status": report.status,
	}


def create_report(record: dict) -> dict:
	with SessionLocal() as db:
		model = Report(
			reporter_id=record.get("reporterId"),
			target_type=record["targetType"],
			target_id=record["targetId"],
			reason=record["reason"],
			status=record.get("status", "open"),
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


def list_reports(page: int = 1, size: int = 20) -> tuple[list[dict], int]:
	with SessionLocal() as db:
		total = db.scalar(select(func.count(Report.id))) or 0
		stmt = (
			select(Report)
			.order_by(Report.created_at.desc(), Report.id.desc())
			.offset((page - 1) * size)
			.limit(size)
		)
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
