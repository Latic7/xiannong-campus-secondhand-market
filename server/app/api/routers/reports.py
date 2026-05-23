from fastapi import APIRouter

from app.core.response import api_ok
from app.schemas.reports import AppealCreateRequest, ReportCreateRequest
from app.services.report_service import (
    create_appeal as create_appeal_service,
    create_report as create_report_service,
    get_report as get_report_service,
)

router = APIRouter(tags=["Report"])


@router.post("/api/reports")
def create_report(payload: ReportCreateRequest) -> dict:
    return api_ok(create_report_service(payload))


@router.get("/api/reports/{report_id}")
def get_report(report_id: int) -> dict:
    return api_ok(get_report_service(report_id))


@router.post("/api/appeals")
def create_appeal(payload: AppealCreateRequest) -> dict:
    return api_ok(create_appeal_service(payload))
