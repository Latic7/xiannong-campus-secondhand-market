from fastapi import APIRouter

from app.core.response import api_ok
from app.schemas.common import AppealCreateRequest, ReportCreateRequest

router = APIRouter(tags=["Report"])


@router.post("/api/reports")
def create_report(payload: ReportCreateRequest) -> dict:
    return api_ok({"id": 7001, **payload.model_dump(), "status": "open"})


@router.get("/api/reports/{report_id}")
def get_report(report_id: int) -> dict:
    return api_ok({"id": report_id, "status": "open"})


@router.post("/api/appeals")
def create_appeal(payload: AppealCreateRequest) -> dict:
    return api_ok({"submitted": True, **payload.model_dump()})
