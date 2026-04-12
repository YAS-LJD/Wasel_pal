from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import TEXT
import enum

from app.database import Base


class ReportCategory(str, enum.Enum):
    checkpoint    = "checkpoint"
    road_closure  = "road_closure"
    delay         = "delay"
    accident      = "accident"
    weather       = "weather"
    other         = "other"


class ReportStatus(str, enum.Enum):
    pending   = "pending"
    accepted  = "accepted"
    rejected  = "rejected"
    duplicate = "duplicate"


class Report(Base):
    __tablename__ = "reports"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude     = Column(Float, nullable=False)
    longitude    = Column(Float, nullable=False)
    category     = Column(SAEnum(ReportCategory, name="report_category", create_type=False), nullable=False)
    description  = Column(TEXT, nullable=True)
    status       = Column(SAEnum(ReportStatus, name="report_status", create_type=False), default=ReportStatus.pending)
    confidence   = Column(Float, default=0.5)
    incident_id  = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    upvotes      = Column(Integer, default=0)
    downvotes    = Column(Integer, default=0)
    moderated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    moderated_at = Column(DateTime, nullable=True)
    created_at   = Column(DateTime, server_default=func.now())