from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.incident import Incident, IncidentCategory, IncidentSeverity, IncidentStatus
from app.models.report import Report, ReportCategory
from app.services.clustering_service import ClusteringService

_CATEGORY_MAP = {
    ReportCategory.checkpoint:   IncidentCategory.other,
    ReportCategory.road_closure: IncidentCategory.closure,
    ReportCategory.delay:        IncidentCategory.delay,
    ReportCategory.accident:     IncidentCategory.accident,
    ReportCategory.weather:      IncidentCategory.weather_hazard,
    ReportCategory.other:        IncidentCategory.other,
}


class ReportService:

    def __init__(self):
        self.clustering = ClusteringService()

    async def create_report(self, db: AsyncSession, user_id: int, data: dict) -> Report:
        report = Report(
            user_id=user_id,
            latitude=data["latitude"],
            longitude=data["longitude"],
            category=data["category"],
            description=data.get("description"),
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)

        await self._run_clustering(db)
        return report

    async def list_reports(self, db: AsyncSession) -> list[Report]:
        result = await db.execute(select(Report).order_by(Report.created_at.desc()))
        return result.scalars().all()

    async def list_my_reports(self, db: AsyncSession, user_id: int) -> list[Report]:
        result = await db.execute(
            select(Report)
            .where(Report.user_id == user_id)
            .order_by(Report.created_at.desc())
        )
        return result.scalars().all()

    async def get_report(self, db: AsyncSession, report_id: int) -> Report | None:
        result = await db.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    async def moderate_report(
        self, db: AsyncSession, report_id: int, moderator_id: int, status: str, confidence: float | None
    ) -> Report | None:
        report = await self.get_report(db, report_id)
        if not report:
            return None
        report.status       = status
        report.moderated_by = moderator_id
        report.moderated_at = datetime.utcnow()
        if confidence is not None:
            report.confidence = confidence
        await db.commit()
        await db.refresh(report)
        return report

    async def vote_report(
        self, db: AsyncSession, report_id: int, vote: str
    ) -> Report | None:
        report = await self.get_report(db, report_id)
        if not report:
            return None
        if vote == "up":
            report.upvotes += 1
        elif vote == "down":
            report.downvotes += 1
        await db.commit()
        await db.refresh(report)
        return report

    async def _run_clustering(self, db: AsyncSession):
        """Fetch pending reports from last 2 hours only, run clustering."""
        # ✅ FIX: Only fetch reports from last 2 hours to limit clustering scope
        two_hours_ago = datetime.utcnow() - timedelta(hours=2)

        result = await db.execute(
            select(Report)
            .where(
                Report.status == "pending",
                Report.created_at >= two_hours_ago  # ← الإصلاح هون
            )
            .limit(500)  # ← حد أقصى 500 report
        )
        reports = result.scalars().all()

        if not reports:
            return

        raw = [
            {
                "id":         r.id,
                "latitude":   float(r.latitude),
                "longitude":  float(r.longitude),
                "category":   r.category,
                "created_at": r.created_at,
            }
            for r in reports
        ]

        clusters = self.clustering.cluster_reports(raw)

        for cluster in clusters:
            if not cluster["should_create_incident"]:
                continue

            category     = cluster["category"]
            category_str = category.value if hasattr(category, "value") else str(category)
            incident_cat = _CATEGORY_MAP.get(category, IncidentCategory.other)

            incident = Incident(
                title=f"Auto-detected: {category_str} cluster ({cluster['size']} reports)",
                description=f"Automatically created from {cluster['size']} clustered reports.",
                category=incident_cat,
                severity=IncidentSeverity.medium,
                status=IncidentStatus.active,
                latitude=cluster["latitude"],
                longitude=cluster["longitude"],
            )
            db.add(incident)
            await db.flush()

            alert = Alert(
                incident_id=incident.id,
                category=category_str,
                message=(
                    f"New incident detected: {category_str} near "
                    f"({cluster['latitude']:.4f}, {cluster['longitude']:.4f}) "
                    f"based on {cluster['size']} reports."
                ),
            )
            db.add(alert)

            report_ids = [r["id"] for r in cluster["reports"]]
            for r in reports:
                if r.id in report_ids:
                    r.incident_id = incident.id

        await db.commit()