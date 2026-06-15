from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.admin_log import AdminLog
from app.models.order import Order
from app.models.product import Product
from app.models.report import Report
from app.models.user import User


def create_admin_log(
    *,
    actor_id: int,
    action: str,
    target_type: str,
    target_id: int,
    remark: str | None = None,
    db: Session | None = None,
) -> None:
    if db is not None:
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
    else:
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


def stats_overview(db: Session | None = None) -> dict:
    """平台运营总览。"""
    def _query(session: Session) -> dict:
        users = session.scalar(select(func.count(User.id))) or 0
        products = session.scalar(select(func.count(Product.id))) or 0
        orders = session.scalar(select(func.count(Order.id))) or 0
        reports = session.scalar(select(func.count(Report.id))) or 0
        return {
            "users": int(users),
            "products": int(products),
            "orders": int(orders),
            "reports": int(reports),
        }

    if db is not None:
        return _query(db)
    with SessionLocal() as db:
        return _query(db)


def _series_with_pct(rows: list, total: int) -> list[dict]:
	"""将 group-by 结果转为带百分比分布的 series。"""
	return [
		{
			"label": str(label),
			"value": int(count),
			"percentage": round(count / total * 100, 1) if total > 0 else 0.0,
		}
		for label, count in rows
	]


def stats_products() -> dict:
	"""商品维度统计。

	按商品状态（status）分组统计数量。
	- series[].label : 商品状态枚举值（如 published, pending, draft, removed, sold）
	- series[].value : 该状态下的商品数量
	- series[].percentage : 该状态占比（%）
	- total           : 商品总数
	- description     : "按商品状态维度统计分布情况"
	"""
	with SessionLocal() as db:
		rows = db.execute(select(Product.status, func.count(Product.id)).group_by(Product.status)).all()
		total = sum(int(count) for _, count in rows) or 0
		return {
			"series": _series_with_pct(rows, total),
			"total": total,
			"dimension": "status",
			"description": "按商品状态维度统计分布情况",
		}


def stats_trades() -> dict:
	"""交易维度统计。

	按订单状态（status）分组统计数量。
	- series[].label : 订单状态枚举值（如 created, reserved, confirmed, completed, cancelled）
	- series[].value : 该状态下的订单数量
	- series[].percentage : 该状态占比（%）
	- total           : 订单总数
	- description     : "按订单状态维度统计交易分布情况"
	"""
	with SessionLocal() as db:
		rows = db.execute(select(Order.status, func.count(Order.id)).group_by(Order.status)).all()
		total = sum(int(count) for _, count in rows) or 0
		return {
			"series": _series_with_pct(rows, total),
			"total": total,
			"dimension": "status",
			"description": "按订单状态维度统计交易分布情况",
		}


def stats_users() -> dict:
	"""用户维度统计。

	按用户状态（status）分组统计数量。
	- series[].label : 用户状态枚举值（如 active, banned）
	- series[].value : 该状态下的用户数量
	- series[].percentage : 该状态占比（%）
	- total           : 用户总数
	- description     : "按用户状态维度统计用户分布情况"
	"""
	with SessionLocal() as db:
		rows = db.execute(select(User.status, func.count(User.id)).group_by(User.status)).all()
		total = sum(int(count) for _, count in rows) or 0
		return {
			"series": _series_with_pct(rows, total),
			"total": total,
			"dimension": "status",
			"description": "按用户状态维度统计用户分布情况",
		}


# 分页查询最大 page_size，防止一次拉取过多数据
_MAX_PAGE_SIZE = 100


def _clamp_size(size: int) -> int:
	"""将 page_size 限制在 [1, _MAX_PAGE_SIZE] 范围内。"""
	return max(1, min(size, _MAX_PAGE_SIZE))


def list_admin_logs(page: int = 1, size: int = 20) -> dict:
	size = _clamp_size(size)
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
