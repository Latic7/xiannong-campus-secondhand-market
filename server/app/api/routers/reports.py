from fastapi import APIRouter, Depends, Query

from app.api.deps.auth import CurrentActor, get_current_actor
from app.core.response import api_ok
from app.schemas.reports import AppealCreateRequest, ReportCreateRequest
from app.services.report_service import (
    create_appeal as create_appeal_service,
    create_report as create_report_service,
    get_report as get_report_service,
    list_my_reports as list_my_reports_service,
)

router = APIRouter(tags=["Report"])


@router.post("/api/reports")
def create_report(
    payload: ReportCreateRequest,
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(create_report_service(payload, actor))


@router.get("/api/reports")
def list_my_reports(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    targetType: str | None = None,
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(list_my_reports_service(actor, page=page, size=size, status=status, target_type=targetType))


@router.get("/api/reports/{report_id}")
def get_report(report_id: int) -> dict:
    return api_ok(get_report_service(report_id))


@router.post("/api/appeals")
def create_appeal(payload: AppealCreateRequest) -> dict:
    return api_ok(create_appeal_service(payload))
