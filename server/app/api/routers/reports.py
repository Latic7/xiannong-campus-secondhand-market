from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.auth import CurrentActor, get_current_actor
from app.core.database import get_db
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
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(
        list_my_reports_service(
            db,
            actor,
            page=page,
            size=size,
            status=status,
            target_type=targetType,
        )
    )


@router.get("/api/reports/against-me")
def list_reports_against_me(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    seenByTarget: str | None = Query(None, pattern=r"^(NOT_SEEN|SEEN)$"),
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    """查询当前用户被举报的记录，可选按 seenByTarget 筛选"""
    from app.services.report_service import list_reports_against_user
    return api_ok(
        list_reports_against_user(
            db,
            actor,
            page=page,
            size=size,
            seen_by_target=seenByTarget,
        )
    )


@router.post("/api/reports/against-me/mark-seen")
def mark_against_me_as_seen(
    db: Session = Depends(get_db),
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    """将当前用户所有被举报记录标记为已读"""
    from app.services.report_service import mark_against_me_as_seen as _mark_seen
    return api_ok(_mark_seen(db, actor))


@router.get("/api/reports/{report_id}")
def get_report(report_id: int) -> dict:
    return api_ok(get_report_service(report_id))


@router.post("/api/appeals")
def create_appeal(
    payload: AppealCreateRequest,
    actor: CurrentActor = Depends(get_current_actor),
) -> dict:
    return api_ok(create_appeal_service(payload, actor))