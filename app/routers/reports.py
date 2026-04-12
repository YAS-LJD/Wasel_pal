from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_moderator
from app.database import get_db
from app.schemas.report import ReportCreate, ReportModerate, ReportResponse, VoteCreate
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])
_svc   = ReportService()


@router.get("", response_model=list[ReportResponse])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_moderator),
):
    """قائمة كل التقارير — Moderator+ فقط"""
    return await _svc.list_reports(db)


@router.get("/my", response_model=list[ReportResponse])
async def my_reports(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """تقارير المستخدم الحالي"""
    return await _svc.list_my_reports(db, current_user["id"])


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    body: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """إرسال تقرير جديد"""
    return await _svc.create_report(db, current_user["id"], body.model_dump())


@router.patch("/{report_id}/moderate", response_model=ReportResponse)
async def moderate_report(
    report_id: int,
    body: ReportModerate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_moderator),
):
    """قبول أو رفض تقرير — Moderator+"""
    report = await _svc.moderate_report(
        db, report_id, current_user["id"], body.status, body.confidence
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/{report_id}/vote", response_model=ReportResponse)
async def vote_report(
    report_id: int,
    body: VoteCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """تصويت على تقرير"""
    if body.vote not in ("up", "down"):
        raise HTTPException(status_code=400, detail="vote must be 'up' or 'down'")
    report = await _svc.vote_report(db, report_id, body.vote)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report