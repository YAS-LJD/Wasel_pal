import enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base


class IncidentCategory(str, enum.Enum):
    closure           = "closure"
    delay             = "delay"
    accident          = "accident"
    weather_hazard    = "weather_hazard"
    military_activity = "military_activity"
    other             = "other"


class IncidentSeverity(str, enum.Enum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"


class IncidentStatus(str, enum.Enum):
    active   = "active"
    verified = "verified"
    resolved = "resolved"
    rejected = "rejected"


class Incident(Base):
    __tablename__ = "incidents"

    id            = Column(Integer, primary_key=True, index=True)
    checkpoint_id = Column(Integer, ForeignKey("checkpoints.id"), nullable=True)
    title         = Column(String(200), nullable=False)
    description   = Column(Text, nullable=True)
    category      = Column(
        SAEnum(IncidentCategory, name="incident_category", create_type=False,
               values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    severity = Column(
        SAEnum(IncidentSeverity, name="incident_severity", create_type=False,
               values_callable=lambda x: [e.value for e in x]),
        default=IncidentSeverity.medium,
    )
    status = Column(
        SAEnum(IncidentStatus, name="incident_status", create_type=False,
               values_callable=lambda x: [e.value for e in x]),
        default=IncidentStatus.active,
    )
    latitude    = Column(Numeric(9, 6), nullable=True)
    longitude   = Column(Numeric(9, 6), nullable=True)
    region      = Column(String(100), nullable=True)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cluster_id  = Column(Integer, nullable=True)
    starts_at   = Column(DateTime, nullable=True)
    ends_at     = Column(DateTime, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())