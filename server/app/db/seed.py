from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin_log import AdminLog
from app.models.order import Order
from app.models.product import Product
from app.models.report import Report
from app.models.stats_daily import StatsDaily
from app.models.user import User


def seed_demo_data(db: Session) -> None:
	has_user = db.scalar(select(User.id).limit(1))
	if has_user is not None:
		return

	db.add_all(
		[
			User(
				id=1,
				openid="wx_openid_demo_1",
				nickname="DemoUser1",
				is_admin=False,
				college="中国农业大学",
				contact="13800000001",
			),
			User(
				id=2,
				openid="wx_openid_demo_2",
				nickname="DemoUser2",
				score=95,
				is_admin=False,
				college="中国农业大学",
				contact="13800000002",
			),
			User(
				id=10,
				openid="wx_openid_admin_10",
				nickname="AdminDemo",
				is_admin=True,
				college="中国农业大学",
				contact="13800000010",
			),
		]
	)

	db.add_all(
		[
			Product(id=1001, owner_id=1, title="二手高数教材", description="九成新，可小刀", price=Decimal("35.00"), category_id=1, status="PUBLISHED", favorite_count=2, view_count=12),
			Product(id=1002, owner_id=1, title="二手计算机网络教材", description="有少量笔记", price=Decimal("28.00"), category_id=1, status="PUBLISHED", favorite_count=1, view_count=5),
			Product(id=1003, owner_id=1, title="二手充电宝", description="容量20000mAh", price=Decimal("45.00"), category_id=2, status="PUBLISHED", favorite_count=0, view_count=3),
		]
	)

	db.add_all(
		[
			Order(id=5001, product_id=1001, buyer_id=2, seller_id=1, amount=Decimal("35.00"), remark="想今晚当面交付", status="CREATED"),
			Order(id=5002, product_id=1002, buyer_id=2, seller_id=1, amount=Decimal("28.00"), remark="明天中午可以吗", status="CONFIRMED"),
		]
	)

	db.add_all(
		[
			Report(id=7001, reporter_id=2, target_type="PRODUCT", target_id=1001, reason="疑似虚假信息", status="OPEN"),
			Report(id=7002, reporter_id=1, target_type="USER", target_id=2, reason="疑似骚扰", status="HANDLED"),
		]
	)

	db.add_all(
		[
			AdminLog(id=9101, actor_id=10, action="warning", target_type="user", target_id=2, remark="测试：管理员警告用户"),
			AdminLog(id=9102, actor_id=10, action="unlist_product", target_type="product", target_id=1003, remark="测试：下架商品"),
			AdminLog(id=9103, actor_id=10, action="handle_report", target_type="report", target_id=7002, remark="测试：处理举报"),
		]
	)

	db.add_all(
		[
			StatsDaily(stat_date=date(2026, 5, 21), users=3, products=4, orders=2, reports=2),
			StatsDaily(stat_date=date(2026, 5, 20), users=2, products=4, orders=2, reports=1),
		]
	)

	db.commit()