from __future__ import annotations

from app.crud.admin import (
	create_admin_log,
	list_admin_logs,
	stats_overview as crud_stats_overview,
	stats_products as crud_stats_products,
	stats_trades as crud_stats_trades,
	stats_users as crud_stats_users,
)
from app.crud.report import get_report as crud_get_report
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


def admin_reports(page: int = 1, size: int = 20, status: str | None = None, target_type: str | None = None) -> dict:
    return list_report_queue(page=page, size=size, status=status, target_type=target_type)


def handle_report(report_id: int, payload) -> dict:
	"""管理员处理举报，记录完整审计信息。

	审计链路：
	- 操作人（actor_id）
	- 操作动作（handle_report:<action>）
	- 目标对象（target_type=report, target_id）
	- 操作原因（remark=payload.reason）
	- 操作时间（created_at 自动记录）
	"""
	result = report_handle_report(report_id, payload)

	# 获取处理后的举报信息，补充审计上下文
	report_data = crud_get_report(report_id)

	# 记录审计日志：action 使用 "handle_report:<具体动作>" 提升可读性
	create_admin_log(
		actor_id=10,  # TODO: 接入登录态后替换为当前管理员 ID
		action=f"handle_report:{payload.action}",
		target_type="report",
		target_id=report_id,
		remark=f"处理举报(#{report_id})：{payload.reason or '无备注'} | 目标类型={report_data.get('targetType') if report_data else '?'}, 目标ID={report_data.get('targetId') if report_data else '?'}",
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
