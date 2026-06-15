from __future__ import annotations

from sqlalchemy.orm import Session

from app.crud.admin import (
    create_admin_log,
    list_admin_logs,
    stats_overview as crud_stats_overview,
    stats_products as crud_stats_products,
    stats_trades as crud_stats_trades,
    stats_users as crud_stats_users,
)
from app.crud.report import get_report as crud_get_report
from app.services import product_service
from app.services.report_service import handle_report as report_handle_report
from app.services.report_service import list_report_queue


def list_users(db: Session, page: int = 1, size: int = 20, keyword: str | None = None) -> dict:
    return {
        "list": [],
        "page": {"page": page, "size": size, "total": 0},
        "keyword": keyword,
    }


def patch_user_status(db: Session, user_id: int, payload) -> dict:
    return {"userId": user_id, **payload.model_dump()}


def pending_products(db: Session, page: int = 1, size: int = 20) -> dict:
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
    return list_report_queue(page=page, size=size, status=status, target_type=target_type)


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


def stats_overview(db: Session) -> dict:
    return crud_stats_overview()


def stats_products(db: Session) -> dict:
    return crud_stats_products()


def stats_trades(db: Session) -> dict:
    return crud_stats_trades()


def stats_users(db: Session) -> dict:
    return crud_stats_users()


def admin_logs(db: Session, page: int = 1, size: int = 20) -> dict:
    return list_admin_logs(page=page, size=size)
