from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_moderator
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/checkpoints")
async def stats_checkpoints(db: AsyncSession = Depends(get_db)):
    """ملخص حالات الحواجز مقسّمة حسب المنطقة والحالة"""
    sql = text("""
        SELECT
            region,
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END)       AS open_count,
            SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END)     AS closed_count,
            SUM(CASE WHEN status = 'restricted' THEN 1 ELSE 0 END) AS restricted_count,
            SUM(CASE WHEN status = 'unknown' THEN 1 ELSE 0 END)    AS unknown_count
        FROM checkpoints
        GROUP BY region
        ORDER BY total DESC
    """)
    result = await db.execute(sql)
    rows = result.mappings().all()
    return {
        "total_checkpoints": sum(r["total"] for r in rows),
        "by_region": [dict(r) for r in rows],
    }


@router.get("/incidents")
async def stats_incidents(db: AsyncSession = Depends(get_db)):
    """إحصائيات الحوادث مقسّمة حسب المنطقة والنوع والخطورة"""
    sql = text("""
        SELECT
            region,
            category,
            severity,
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END)     AS open_count,
            SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) AS resolved_count
        FROM incidents
        GROUP BY region, category, severity
        ORDER BY total DESC
    """)
    result = await db.execute(sql)
    rows = result.mappings().all()
    return {
        "total_incidents": sum(r["total"] for r in rows),
        "breakdown": [dict(r) for r in rows],
    }


@router.get("/reports")
async def stats_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator),
):
    """حجم التقارير — للمشرفين فقط"""
    sql = text("""
        SELECT
            status,
            COUNT(*) AS total
        FROM reports
        GROUP BY status
        ORDER BY total DESC
    """)
    result = await db.execute(sql)
    rows = result.mappings().all()

    vote_sql = text("SELECT COUNT(*) AS total FROM report_votes")
    vote_result = await db.execute(vote_sql)
    total_votes = vote_result.scalar()

    return {
        "reports_by_status": [dict(r) for r in rows],
        "total_votes": total_votes,
    }