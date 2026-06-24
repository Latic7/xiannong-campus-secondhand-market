from __future__ import annotations

from sqlalchemy.orm import Session

from app.api.deps.auth import CurrentActor
from app.core.exceptions import InvalidRequestError, ResourceNotFoundError
from app.crud.report import create_report as crud_create_report
from app.crud.report import get_report as crud_get_report
from app.crud.report import list_reports_with_target as crud_list_reports_with_target
from app.crud.report import update_report as crud_update_report
from app.models.product import Product
from app.models.user import User
from app.schemas.admin import ReportHandleRequest
from app.schemas.reports import AppealCreateRequest, ReportCreateRequest


def create_report(payload: ReportCreateRequest, actor: CurrentActor | None = None) -> dict:
    from app.core.database import SessionLocal
    from app.core.status import ProductStatus

    # 举报商品时，只允许针对"在售"商品
    if payload.targetType == "PRODUCT":
        with SessionLocal() as db:
            product = db.get(Product, payload.targetId)
            if product is None:
                raise ResourceNotFoundError("商品不存在")
            if product.status != ProductStatus.PUBLISHED.value:
                raise InvalidRequestError("只能举报在售中的商品")

    reporter_id = actor.user_id if actor else 3
    report = crud_create_report(
        {
            **payload.model_dump(),
            "reporterId": reporter_id,
            "status": "OPEN",
        }
    )
    return report


def get_report(report_id: int) -> dict:
    report = crud_get_report(report_id)
    if report is None:
        raise ResourceNotFoundError(f"举报记录 {report_id} 不存在")
    return report


def list_report_queue(
	db: Session,
	page: int = 1,
	size: int = 20,
	status: str | None = None,
	target_type: str | None = None,
) -> dict:
	rows, total = crud_list_reports_with_target(
		db,
		page=page,
		size=size,
		status=status,
		target_type=target_type,
	)
	return {
		"list": rows,
		"page": {"page": page, "size": size, "total": total},
	}


def list_my_reports(
    db: Session,
    actor: CurrentActor,
    page: int = 1,
    size: int = 20,
    status: str | None = None,
    target_type: str | None = None,
) -> dict:
    # 与举报队列一致，附带被举报对象摘要，供前端富卡片展示
    rows, total = crud_list_reports_with_target(
        db,
        page=page,
        size=size,
        status=status,
        target_type=target_type,
        reporter_id=actor.user_id,
    )
    return {
        "list": rows,
        "page": {"page": page, "size": size, "total": total},
        "filters": {"status": status, "targetType": target_type},
    }


def handle_report(report_id: int, payload: ReportHandleRequest, actor: CurrentActor | None = None) -> dict:
    from app.core.database import SessionLocal
    from app.models.user import User

    status = "REJECTED" if payload.action == "reject" else "HANDLED"
    assignee_id = actor.user_id if actor else 10

    # 获取举报记录，找出被举报人并扣除信誉分
    report = crud_get_report(report_id)
    if report is None:
        raise ResourceNotFoundError(f"举报记录 {report_id} 不存在，无法处理")

    with SessionLocal() as db:
        # 根据举报类型找出目标用户
        target_user_id = None
        if report["targetType"] == "USER":
            target_user_id = report["targetId"]
        elif report["targetType"] == "PRODUCT":
            product = db.get(Product, report["targetId"])
            if product:
                target_user_id = product.owner_id

        # 如果处理动作不是驳回，扣除被举报人信誉分
        if payload.action != "reject" and target_user_id:
            user = db.get(User, target_user_id)
            if user:
                if payload.action == "ban_user":
                    user.score = 0  # 封禁直接清零
                else:
                    deduction = {"warning": 5, "unlist_product": 15}.get(payload.action, 10)
                    user.score = max(0, min(100, (user.score or 100) - deduction))

        # 下架商品：将目标商品状态设为 REMOVED
        if payload.action == "unlist_product" and report["targetType"] == "PRODUCT":
            product = db.get(Product, report["targetId"])
            if product and product.status != "REMOVED":
                product.status = "REMOVED"

        db.commit()

    updated = crud_update_report(
        report_id,
        {
            "status": status,
            "action": payload.action,
            "reason": payload.reason,
            "assigneeId": assignee_id,
        },
    )
    if updated is None:
        raise ResourceNotFoundError(f"举报记录 {report_id} 不存在，无法处理")

    return {"reportId": report_id, **payload.model_dump()}


def list_reports_against_user(
    db: Session,
    actor: CurrentActor,
    page: int = 1,
    size: int = 20,
    seen_by_target: str | None = None,
) -> dict:
    """查询针对当前用户的举报（通过被举报对象关联）"""
    from app.models.report import Report as ReportModel
    from sqlalchemy import or_

    rows, total = crud_list_reports_with_target(
        db,
        page=page,
        size=size,
        target_user_id=actor.user_id,
        seen_by_target=seen_by_target,
    )
    return {
        "list": rows,
        "page": {"page": page, "size": size, "total": total},
    }


def mark_against_me_as_seen(db: Session, actor: CurrentActor) -> dict:
    """将当前用户被举报的所有记录的 seen_by_target 置为 SEEN"""
    from app.models.report import Report as ReportModel
    from app.models.product import Product
    from sqlalchemy import or_, select, update

    # 找出该用户的商品 ID
    product_ids = db.scalars(
        select(Product.id).where(Product.owner_id == actor.user_id)
    ).all()

    rows = db.scalars(
        select(ReportModel).where(
            or_(
                (ReportModel.target_type == "USER") & (ReportModel.target_id == actor.user_id),
                (ReportModel.target_type == "PRODUCT") & (ReportModel.target_id.in_(product_ids)),
            ),
            ReportModel.seen_by_target == "NOT_SEEN",
        )
    ).all()

    count = len(rows)
    for r in rows:
        r.seen_by_target = "SEEN"
    db.commit()

    return {"markedCount": count}


def create_appeal(payload: AppealCreateRequest) -> dict:
    return {"submitted": True, **payload.model_dump()}
