from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.admin import (
    create_admin_log,
    list_admin_logs,
    stats_overview as crud_stats_overview,
    stats_products as crud_stats_products,
    stats_trades as crud_stats_trades,
    stats_users as crud_stats_users,
    stats_trends as crud_stats_trends,
    stats_categories as crud_stats_categories,
)
from app.crud.report import get_report as crud_get_report
from app.services import product_service
from app.services.report_service import handle_report as report_handle_report
from app.services.report_service import list_report_queue


def list_users(db: Session, page: int = 1, size: int = 20, keyword: str | None = None, status: str | None = None) -> dict:
    from app.models.user import User
    from sqlalchemy import select, func

    stmt = select(User)
    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(User.nickname.ilike(kw) | User.openid.ilike(kw))
    if status:
        stmt = stmt.where(User.status == status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(User.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = [
        {
            "id": u.id,
            "nickname": u.nickname,
            "avatar": u.avatar,
            "score": u.score,
            "status": u.status,
            "isAdmin": u.is_admin,
            "createdAt": u.created_at.isoformat() if u.created_at else None,
        }
        for u in rows
    ]
    return {"list": items, "page": {"page": page, "size": size, "total": int(total)}}


def patch_user_status(db: Session, user_id: int, payload) -> dict:
    from app.models.user import User as UserModel
    user = db.get(UserModel, user_id)
    if user is None:
        from app.core.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("user not found", {"userId": user_id})
    user.status = payload.status
    if payload.status == "BANNED":
        user.score = 0
    elif payload.status == "ACTIVE":
        user.score = 20  # 解封后赋予基础信誉分
    db.commit()
    return {"userId": user_id, "status": payload.status, "score": user.score}


def pending_products(db: Session, page: int = 1, size: int = 20, status: str | None = None) -> dict:
    if status:
        return product_service.list_pending_products(db, page, size, status=status)
    return product_service.list_pending_products(db, page, size)


def review_product(db: Session, product_id: int, payload) -> dict:
    result = product_service.review_product(db, product_id, payload.result, payload.reason)
    create_admin_log(
        db=db,
        actor_id=10,
        action=f"review_product_{payload.result}",
        target_type="product",
        target_id=product_id,
        remark=payload.reason,
    )
    return result


def admin_reports(
	db: Session,
	page: int = 1,
	size: int = 20,
	status: str | None = None,
	target_type: str | None = None,
) -> dict:
	# 支持逗号分隔的多个状态值
	status_list = [s.strip() for s in status.split(",") if s.strip()] if status else None
	return list_report_queue(db, page=page, size=size, status=status_list, target_type=target_type)


def handle_report(db: Session, report_id: int, payload) -> dict:
    result = report_handle_report(report_id, payload)
    report_data = crud_get_report(report_id)
    create_admin_log(
        db=db,
        actor_id=10,
        action=f"handle_report:{payload.action}",
        target_type="report",
        target_id=report_id,
        remark=(
            f"report #{report_id}: {payload.reason or 'no remark'} | "
            f"target={report_data.get('targetType') if report_data else '?'}:"
            f"{report_data.get('targetId') if report_data else '?'}"
        ),
    )
    return result


def stats_overview(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
    return crud_stats_overview(db, start_date=start_date, end_date=end_date)


def stats_products(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
    return crud_stats_products(db, start_date=start_date, end_date=end_date)


def stats_trades(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
    return crud_stats_trades(db, start_date=start_date, end_date=end_date)


def stats_users(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
    return crud_stats_users(db, start_date=start_date, end_date=end_date)


def admin_logs(db: Session, page: int = 1, size: int = 20, start_date: str | None = None, end_date: str | None = None) -> dict:
    return list_admin_logs(db, page=page, size=size, start_date=start_date, end_date=end_date)


def stats_trends(db: Session, start_date: str | None = None, end_date: str | None = None) -> dict:
    return crud_stats_trends(db, start_date=start_date, end_date=end_date)


def stats_categories(db: Session) -> dict:
    return crud_stats_categories(db)
