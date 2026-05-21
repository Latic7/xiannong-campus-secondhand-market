from fastapi import APIRouter

from app.core.response import api_ok
<<<<<<< HEAD
from app.core.status import ReportStatus
from app.schemas.common import AppealCreateRequest, ReportCreateRequest
=======
from app.schemas.reports import AppealCreateRequest, ReportCreateRequest
from app.services.report_service import (
    create_appeal as create_appeal_service,
    create_report as create_report_service,
    get_report as get_report_service,
)
>>>>>>> 7802987 (release: release branch for the first time)

router = APIRouter(tags=["Report"])


@router.post("/api/reports")
def create_report(payload: ReportCreateRequest) -> dict:
<<<<<<< HEAD
    return api_ok({"id": 7001, **payload.model_dump(), "status": ReportStatus.OPEN.value})
=======
    return api_ok(create_report_service(payload))
>>>>>>> 7802987 (release: release branch for the first time)


@router.get("/api/reports/{report_id}")
def get_report(report_id: int) -> dict:
<<<<<<< HEAD
    return api_ok({"id": report_id, "status": ReportStatus.OPEN.value})
=======
    return api_ok(get_report_service(report_id))
>>>>>>> 7802987 (release: release branch for the first time)


@router.post("/api/appeals")
def create_appeal(payload: AppealCreateRequest) -> dict:
    return api_ok(create_appeal_service(payload))
