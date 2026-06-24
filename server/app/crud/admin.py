from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.admin_log import AdminLog
from app.models.category import Category
from app.models.order import Order
from app.models.product import Product
from app.models.report import Report
from app.models.user import User


def _parse_date_range(start_date: str | None, end_date: str | None):
    """将 YYYY-MM-DD 字符串转为 datetime 范围，供 SQLAlchemy 过滤。"""
    from_date = None
    to_date = None
    if start_date:
        try:
            from_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            pass
    if end_date:
        try:
            # 结束日期取当天末尾 23:59:59
            to_date = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except ValueError:
            pass
    return from_date, to_date


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


def stats_overview(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
    """平台运营总览。"""
    from_dt, to_dt = _parse_date_range(start_date, end_date)

    def _count(model, time_col=None):
        stmt = select(func.count(model.id))
        if time_col is not None:
            if from_dt:
                stmt = stmt.where(time_col >= from_dt)
            if to_dt:
                stmt = stmt.where(time_col <= to_dt)
        return int(db.scalar(stmt) or 0)

    return {
        "users": _count(User, User.created_at),
        "products": _count(Product, Product.created_at),
        "orders": _count(Order, Order.created_at),
        "reports": _count(Report, Report.created_at),
    }


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


def stats_products(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
	"""商品维度统计。

	按商品状态（status）分组统计数量。
	- series[].label : 商品状态枚举值（如 published, pending, draft, removed, sold）
	- series[].value : 该状态下的商品数量
	- series[].percentage : 该状态占比（%）
	- total           : 商品总数
	- description     : "按商品状态维度统计分布情况"
	"""
	from_dt, to_dt = _parse_date_range(start_date, end_date)
	stmt = select(Product.status, func.count(Product.id)).group_by(Product.status)
	if from_dt:
		stmt = stmt.where(Product.created_at >= from_dt)
	if to_dt:
		stmt = stmt.where(Product.created_at <= to_dt)
	rows = db.execute(stmt).all()
	total = sum(int(count) for _, count in rows) or 0
	return {
		"series": _series_with_pct(rows, total),
		"total": total,
		"dimension": "status",
		"description": "按商品状态维度统计分布情况",
	}


def stats_trades(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
	"""交易维度统计。

	按订单状态（status）分组统计数量。
	- series[].label : 订单状态枚举值（如 created, reserved, confirmed, completed, cancelled）
	- series[].value : 该状态下的订单数量
	- series[].percentage : 该状态占比（%）
	- total           : 订单总数
	- description     : "按订单状态维度统计交易分布情况"
	"""
	from_dt, to_dt = _parse_date_range(start_date, end_date)
	stmt = select(Order.status, func.count(Order.id)).group_by(Order.status)
	if from_dt:
		stmt = stmt.where(Order.created_at >= from_dt)
	if to_dt:
		stmt = stmt.where(Order.created_at <= to_dt)
	rows = db.execute(stmt).all()
	total = sum(int(count) for _, count in rows) or 0
	return {
		"series": _series_with_pct(rows, total),
		"total": total,
		"dimension": "status",
		"description": "按订单状态维度统计交易分布情况",
	}


def stats_users(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
	"""用户维度统计。

	按用户状态（status）分组统计数量。
	- series[].label : 用户状态枚举值（如 active, banned）
	- series[].value : 该状态下的用户数量
	- series[].percentage : 该状态占比（%）
	- total           : 用户总数
	- description     : "按用户状态维度统计用户分布情况"
	"""
	from_dt, to_dt = _parse_date_range(start_date, end_date)
	stmt = select(User.status, func.count(User.id)).group_by(User.status)
	if from_dt:
		stmt = stmt.where(User.created_at >= from_dt)
	if to_dt:
		stmt = stmt.where(User.created_at <= to_dt)
	rows = db.execute(stmt).all()
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


def list_admin_logs(db: Session, page: int = 1, size: int = 20, start_date: str | None = None, end_date: str | None = None) -> dict:
	size = _clamp_size(size)
	from_dt, to_dt = _parse_date_range(start_date, end_date)
	total = db.scalar(select(func.count(AdminLog.id))) or 0
	stmt = select(AdminLog)
	if from_dt:
		stmt = stmt.where(AdminLog.created_at >= from_dt)
	if to_dt:
		stmt = stmt.where(AdminLog.created_at <= to_dt)
	stmt = stmt.order_by(AdminLog.created_at.desc(), AdminLog.id.desc())
	stmt = stmt.offset((page - 1) * size).limit(size)
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


def stats_trends(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
	"""每日趋势统计：商品发布数、成交订单数、用户注册数。"""
	from_dt, to_dt = _parse_date_range(start_date, end_date)

	def _daily(model, time_col, label_field=None):
		date_col = func.date(time_col)
		stmt = select(date_col, func.count(model.id)).group_by(date_col).order_by(date_col)
		if from_dt:
			stmt = stmt.where(time_col >= from_dt)
		if to_dt:
			stmt = stmt.where(time_col <= to_dt)
		rows = db.execute(stmt).all()
		return [{"date": str(row[0]), "value": int(row[1])} for row in rows]

	return {
		"productTrend": _daily(Product, Product.created_at),
		"orderTrend": _daily(Order, Order.created_at),
		"userTrend": _daily(User, User.created_at),
	}


def stats_categories(db: Session) -> dict:
	"""热门商品类别：按商品分类统计在售商品数量。"""
	stmt = (
		select(Category.name, func.count(Product.id))
		.outerjoin(Product, Product.category_id == Category.id)
		.group_by(Category.id, Category.name)
		.order_by(func.count(Product.id).desc())
	)
	rows = db.execute(stmt).all()
	total = sum(int(row[1]) for row in rows) or 0
	return {
		"series": [
			{"label": str(row[0]), "value": int(row[1]), "percentage": round(row[1] / total * 100, 1) if total > 0 else 0.0}
			for row in rows
		],
		"total": total,
		"description": "按商品分类统计在售商品分布情况",
	}
