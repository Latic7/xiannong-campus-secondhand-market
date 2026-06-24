from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.response import api_ok
from app.core.database import get_db
from app.api.deps.admin import get_current_admin  # 注意导入路径
from app.schemas.admin import ProductReviewRequest, ReportHandleRequest, UserStatusPatchRequest
from app.services.admin_service import (
    admin_logs as admin_logs_service,
    admin_reports as admin_reports_service,
    handle_report as handle_report_service,
    list_users as list_users_service,
    pending_products as pending_products_service,
    patch_user_status as patch_user_status_service,
    review_product as review_product_service,
    stats_overview as stats_overview_service,
    stats_products as stats_products_service,
    stats_trades as stats_trades_service,
    stats_users as stats_users_service,
    stats_trends as stats_trends_service,
    stats_categories as stats_categories_service,
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users")
def admin_list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
    status: str | None = Query(None, description="用户状态筛选"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(list_users_service(db, page=page, size=size, keyword=keyword, status=status))


@router.patch("/users/{user_id}/status")
def patch_user_status(
    user_id: int,
    payload: UserStatusPatchRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(patch_user_status_service(db, user_id, payload))


@router.get("/products/pending")
def pending_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, description="商品状态筛选，为空则默认 PENDING"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(pending_products_service(db, page=page, size=size, status=status))


@router.post("/products/{product_id}/review")
def review_product(
    product_id: int,
    payload: ProductReviewRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(review_product_service(db, product_id, payload))


@router.get("/reports")
def admin_reports(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    target_type: str | None = None,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(
        admin_reports_service(
            db,
            page=page,
            size=size,
            status=status,
            target_type=target_type,
        )
    )


@router.post("/reports/{report_id}/handle")
def handle_report(
    report_id: int,
    payload: ReportHandleRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(handle_report_service(db, report_id, payload))


@router.get("/stats/overview")
def stats_overview(
    startDate: str | None = Query(None, description="起始日期，格式 YYYY-MM-DD"),
    endDate: str | None = Query(None, description="结束日期，格式 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(stats_overview_service(db, start_date=startDate, end_date=endDate))


@router.get("/stats/products")
def stats_products(
    startDate: str | None = Query(None, description="起始日期，格式 YYYY-MM-DD"),
    endDate: str | None = Query(None, description="结束日期，格式 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(stats_products_service(db, start_date=startDate, end_date=endDate))


@router.get("/stats/trades")
def stats_trades(
    startDate: str | None = Query(None, description="起始日期，格式 YYYY-MM-DD"),
    endDate: str | None = Query(None, description="结束日期，格式 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(stats_trades_service(db, start_date=startDate, end_date=endDate))


@router.get("/stats/users")
def stats_users(
    startDate: str | None = Query(None, description="起始日期，格式 YYYY-MM-DD"),
    endDate: str | None = Query(None, description="结束日期，格式 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(stats_users_service(db, start_date=startDate, end_date=endDate))


@router.get("/stats/trends")
def stats_trends(
    startDate: str | None = Query(None, description="起始日期，格式 YYYY-MM-DD"),
    endDate: str | None = Query(None, description="结束日期，格式 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(stats_trends_service(db, start_date=startDate, end_date=endDate))


@router.get("/stats/categories")
def stats_categories(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(stats_categories_service(db))


@router.get("/logs")
def admin_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    startDate: str | None = Query(None, description="起始日期，格式 YYYY-MM-DD"),
    endDate: str | None = Query(None, description="结束日期，格式 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin),
) -> dict:
    return api_ok(admin_logs_service(db, page=page, size=size, start_date=startDate, end_date=endDate))
