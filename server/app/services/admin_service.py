from __future__ import annotations

from app.crud.admin import (
	create_admin_log,
	list_admin_logs,
	list_reports,
	stats_overview as crud_stats_overview,
	stats_products as crud_stats_products,
	stats_trades as crud_stats_trades,
	stats_users as crud_stats_users,
)
from app.services.report_service import handle_report as report_handle_report
from app.services.report_service import list_report_queue


def list_users(page: int = 1, size: int = 20, keyword: str | None = None) -> dict:
	return {
		"list": [],
		"page": {"page": page, "size": size, "total": 0},
		"keyword": keyword,
	}


def patch_user_status(user_id: int, payload) -> dict:
	return {"userId": user_id, **payload.model_dump()}


def pending_products(page: int = 1, size: int = 20) -> dict:
	return {"list": [], "page": {"page": page, "size": size, "total": 0}}


def review_product(product_id: int, payload) -> dict:
	return {"productId": product_id, **payload.model_dump()}


def admin_reports(page: int = 1, size: int = 20) -> dict:
    return list_report_queue(page=page, size=size)


def handle_report(report_id: int, payload) -> dict:
	result = report_handle_report(report_id, payload)
	create_admin_log(
		actor_id=10,
		action=payload.action,
		target_type="report",
		target_id=result["reportId"],
		remark=payload.reason,
	)
	return result


def stats_overview() -> dict:
    return crud_stats_overview()


def stats_products() -> dict:
    return crud_stats_products()


def stats_trades() -> dict:
    return crud_stats_trades()


def stats_users() -> dict:
    return crud_stats_users()


def admin_logs(page: int = 1, size: int = 20) -> dict:
    return list_admin_logs(page=page, size=size)
