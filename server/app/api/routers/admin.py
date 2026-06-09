from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import api_ok
from app.core.database import get_db
from app.core.dependencies import get_current_admin  # 新增
from app.models.user import User  # 新增
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
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users")
def admin_list_users(
    page: int = 1, 
    size: int = 20, 
    keyword: str | None = None,
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(list_users_service(db, page=page, size=size, keyword=keyword))


@router.patch("/users/{user_id}/status")
def patch_user_status(
    user_id: int, 
    payload: UserStatusPatchRequest,
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(patch_user_status_service(db, user_id, payload))


@router.get("/products/pending")
def pending_products(
    page: int = 1, 
    size: int = 20,
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(pending_products_service(db, page=page, size=size))


@router.post("/products/{product_id}/review")
def review_product(
    product_id: int, 
    payload: ProductReviewRequest,
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(review_product_service(db, product_id, payload))


@router.get("/reports")
def admin_reports(
    page: int = 1, 
    size: int = 20,
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(admin_reports_service(db, page=page, size=size))


@router.post("/reports/{report_id}/handle")
def handle_report(
    report_id: int, 
    payload: ReportHandleRequest,
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(handle_report_service(db, report_id, payload))


@router.get("/stats/overview")
def stats_overview(
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(stats_overview_service(db))


@router.get("/stats/products")
def stats_products(
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(stats_products_service(db))


@router.get("/stats/trades")
def stats_trades(
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(stats_trades_service(db))


@router.get("/stats/users")
def stats_users(
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(stats_users_service(db))


@router.get("/logs")
def admin_logs(
    page: int = 1, 
    size: int = 20,
    current_admin: User = Depends(get_current_admin),  # 新增
    db: Session = Depends(get_db),  # 新增
) -> dict:
    return api_ok(admin_logs_service(db, page=page, size=size))