from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.order import Order
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.report import Report
from app.models.user import User


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
	reporter_id: int | None = None,
) -> tuple[list[dict], int]:
	"""分页查询举报列表，支持按 status 和 target_type 筛选。"""
	size = _clamp_size(size)
	with SessionLocal() as db:
		filters = []
		if status:
			filters.append(Report.status == status)
		if target_type:
			filters.append(Report.target_type == target_type)
		if reporter_id is not None:
			filters.append(Report.reporter_id == reporter_id)

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


# ── 举报对象摘要 ─────────────────────────────────
# 后台举报队列需要展示被举报对象的详细信息（商品图片/标题/价格、
# 用户昵称/头像、订单金额等），便于管理员快速识别与处理。


def _product_target_summary(db: Session, product_id: int) -> dict | None:
	"""商品摘要：图片、标题、价格、状态、所属卖家。"""
	product = db.get(Product, product_id)
	if product is None:
		return None
	image = db.scalar(
		select(ProductImage.url)
		.where(ProductImage.product_id == product_id)
		.order_by(ProductImage.id)
		.limit(1)
	)
	seller = None
	if product.owner_id:
		owner = db.get(User, product.owner_id)
		seller = {
			"id": owner.id,
			"nickname": owner.nickname or "未知用户",
		} if owner else None
	return {
		"id": product.id,
		"title": product.title,
		"price": float(product.price) if product.price is not None else None,
		"image": image or "",
		"status": product.status,
		"seller": seller,
	}


def _user_target_summary(db: Session, user_id: int) -> dict | None:
	"""用户摘要：昵称、头像、状态、信用分。"""
	user = db.get(User, user_id)
	if user is None:
		return None
	return {
		"id": user.id,
		"nickname": user.nickname or "未知用户",
		"avatar": user.avatar or "",
		"status": user.status,
		"score": user.score,
	}


def _order_target_summary(db: Session, order_id: int) -> dict | None:
	"""订单摘要：金额、状态，并附带关联商品摘要。"""
	order = db.get(Order, order_id)
	if order is None:
		return None
	return {
		"id": order.id,
		"amount": float(order.amount) if order.amount is not None else None,
		"status": order.status,
		"product": _product_target_summary(db, order.product_id),
	}


def _target_summary(db: Session, report: Report) -> dict | None:
	"""根据举报类型返回对应对象的摘要，找不到时返回 None。"""
	if report.target_type == "PRODUCT":
		return _product_target_summary(db, report.target_id)
	if report.target_type == "USER":
		return _user_target_summary(db, report.target_id)
	if report.target_type == "ORDER":
		return _order_target_summary(db, report.target_id)
	return None


def list_reports_with_target(
	db: Session,
	page: int = 1,
	size: int = 20,
	status: str | None = None,
	target_type: str | None = None,
	reporter_id: int | None = None,
	target_user_id: int | None = None,
) -> tuple[list[dict], int]:
	"""分页查询举报列表，并为每条记录附上被举报对象摘要。

	参数 target_user_id 用于查询针对某个用户的举报（被举报人是该用户，
	或被举报商品属于该用户）。
	"""
	size = _clamp_size(size)
	filters = []
	if status:
		filters.append(Report.status == status)
	if target_type:
		filters.append(Report.target_type == target_type)
	if reporter_id is not None:
		filters.append(Report.reporter_id == reporter_id)
	if target_user_id is not None:
		# 查询针对该用户的举报：直接举报用户 OR 举报的商品属于该用户
		from sqlalchemy import or_
		user_product_ids = db.scalars(
			select(Product.id).where(Product.owner_id == target_user_id)
		).all()
		filters.append(
			or_(
				(Report.target_type == "USER") & (Report.target_id == target_user_id),
				(Report.target_type == "PRODUCT") & (Report.target_id.in_(user_product_ids)),
			)
		)

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
	result = []
	for row in rows:
		item = _to_schema_dict(row)
		item["target"] = _target_summary(db, row)
		result.append(item)
	return result, int(total)


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
