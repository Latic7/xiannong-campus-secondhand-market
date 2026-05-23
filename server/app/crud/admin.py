from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.admin_log import AdminLog
from app.models.order import Order
from app.models.product import Product
from app.models.report import Report
from app.models.user import User


def list_reports(page: int = 1, size: int = 20) -> dict:
	with SessionLocal() as db:
		total = db.scalar(select(func.count(Report.id))) or 0
		stmt = (
			select(Report)
			.order_by(Report.created_at.desc(), Report.id.desc())
			.offset((page - 1) * size)
			.limit(size)
		)
		rows = db.scalars(stmt).all()
		items = [
			{
				"id": row.id,
				"reporterId": row.reporter_id,
				"targetType": row.target_type,
				"targetId": row.target_id,
				"reason": row.reason,
				"status": row.status,
			}
			for row in rows
		]
		return {"list": items, "page": {"page": page, "size": size, "total": int(total)}}


def create_admin_log(*, actor_id: int, action: str, target_type: str, target_id: int, remark: str | None = None) -> None:
	with SessionLocal() as db:
		db.add(
			AdminLog(
				actor_id=actor_id,
				action=action,
				target_type=target_type,
				target_id=target_id,
				remark=remark,
				created_at=datetime.now(timezone.utc),
			)
		)
		db.commit()


def stats_overview() -> dict:
	with SessionLocal() as db:
		users = db.scalar(select(func.count(User.id))) or 0
		products = db.scalar(select(func.count(Product.id))) or 0
		orders = db.scalar(select(func.count(Order.id))) or 0
		reports = db.scalar(select(func.count(Report.id))) or 0
		return {
			"users": int(users),
			"products": int(products),
			"orders": int(orders),
			"reports": int(reports),
		}


def stats_products() -> dict:
	with SessionLocal() as db:
		rows = db.execute(select(Product.status, func.count(Product.id)).group_by(Product.status)).all()
		series = [{"label": str(status), "value": int(count)} for status, count in rows]
		total = sum(item["value"] for item in series)
		return {"series": series, "total": total}


def stats_trades() -> dict:
	with SessionLocal() as db:
		rows = db.execute(select(Order.status, func.count(Order.id)).group_by(Order.status)).all()
		series = [{"label": str(status), "value": int(count)} for status, count in rows]
		total = sum(item["value"] for item in series)
		return {"series": series, "total": total}


def stats_users() -> dict:
	with SessionLocal() as db:
		rows = db.execute(select(User.status, func.count(User.id)).group_by(User.status)).all()
		series = [{"label": str(status), "value": int(count)} for status, count in rows]
		total = sum(item["value"] for item in series)
		return {"series": series, "total": total}


def list_admin_logs(page: int = 1, size: int = 20) -> dict:
	with SessionLocal() as db:
		total = db.scalar(select(func.count(AdminLog.id))) or 0
		stmt = (
			select(AdminLog)
			.order_by(AdminLog.created_at.desc(), AdminLog.id.desc())
			.offset((page - 1) * size)
			.limit(size)
		)
		rows = db.scalars(stmt).all()
		items = [
			{
				"id": row.id,
				"actorId": row.actor_id,
				"action": row.action,
				"targetType": row.target_type,
				"targetId": row.target_id,
				"remark": row.remark,
				"createdAt": row.created_at.isoformat(),
			}
			for row in rows
		]
		return {"list": items, "page": {"page": page, "size": size, "total": int(total)}}
