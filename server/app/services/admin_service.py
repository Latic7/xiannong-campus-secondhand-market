from __future__ import annotations

from datetime import datetime, timezone


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
	return {"list": [], "page": {"page": page, "size": size, "total": 0}}


def handle_report(report_id: int, payload) -> dict:
	return {"reportId": report_id, **payload.model_dump()}


def stats_overview() -> dict:
	return {"users": 132, "products": 67, "orders": 28, "reports": 3}


def stats_products() -> dict:
	return {
		"series": [
			{"label": "published", "value": 42},
			{"label": "pending", "value": 8},
			{"label": "removed", "value": 17},
		],
		"total": 67,
	}


def stats_trades() -> dict:
	return {
		"series": [
			{"label": "created", "value": 12},
			{"label": "completed", "value": 9},
			{"label": "cancelled", "value": 7},
		],
		"total": 28,
	}


def stats_users() -> dict:
	return {
		"series": [
			{"label": "active", "value": 120},
			{"label": "banned", "value": 12},
		],
		"total": 132,
	}


def admin_logs(page: int = 1, size: int = 20) -> dict:
	now = datetime.now(timezone.utc).isoformat()
	logs = [
		{
			"id": 9001,
			"actorId": 10,
			"action": "ban_user",
			"targetType": "user",
			"targetId": 2,
			"remark": "多次违规",
			"createdAt": now,
		}
	]
	return {"list": logs, "page": {"page": page, "size": size, "total": len(logs)}}
