from fastapi import APIRouter

from app.core.response import api_ok
from app.schemas.common import ProductReviewRequest, ReportHandleRequest, UserStatusPatchRequest

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users")
def admin_list_users(page: int = 1, size: int = 20, keyword: str | None = None) -> dict:
    return api_ok(
        {
            "list": [],
            "page": {"page": page, "size": size, "total": 0},
            "keyword": keyword,
        }
    )


@router.patch("/users/{user_id}/status")
def patch_user_status(user_id: int, payload: UserStatusPatchRequest) -> dict:
    return api_ok({"userId": user_id, "status": payload.status.value, "reason": payload.reason})


@router.get("/products/pending")
def pending_products(page: int = 1, size: int = 20) -> dict:
    return api_ok({"list": [], "page": {"page": page, "size": size, "total": 0}})


@router.post("/products/{product_id}/review")
def review_product(product_id: int, payload: ProductReviewRequest) -> dict:
    return api_ok({"productId": product_id, **payload.model_dump()})


@router.get("/reports")
def admin_reports(page: int = 1, size: int = 20) -> dict:
    return api_ok({"list": [], "page": {"page": page, "size": size, "total": 0}})


@router.post("/reports/{report_id}/handle")
def handle_report(report_id: int, payload: ReportHandleRequest) -> dict:
    return api_ok({"reportId": report_id, **payload.model_dump()})


@router.get("/stats/overview")
def stats_overview() -> dict:
    return api_ok({"users": 0, "products": 0, "orders": 0, "reports": 0})


@router.get("/stats/products")
def stats_products() -> dict:
    return api_ok({"series": []})


@router.get("/stats/trades")
def stats_trades() -> dict:
    return api_ok({"series": []})


@router.get("/stats/users")
def stats_users() -> dict:
    return api_ok({"series": []})


@router.get("/logs")
def admin_logs(page: int = 1, size: int = 20) -> dict:
    return api_ok({"list": [], "page": {"page": page, "size": size, "total": 0}})
