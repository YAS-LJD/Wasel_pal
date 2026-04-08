import enum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base


class IncidentCategory(str, enum.Enum):
    arrest = "arrest"
    shooting = "shooting"
    road_block = "road_block"
    tear_gas = "tear_gas"
    settler_attack = "settler_attack"
    other = "other"


class IncidentSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatus(str, enum.Enum):
    open = "open"
    verified = "verified"
    resolved = "resolved"
    rejected = "rejected"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    region = Column(String(100), nullable=True)
    category = Column(
        SAEnum(IncidentCategory, name="incident_category", create_type=False),
        default=IncidentCategory.other,
    )
    severity = Column(
        SAEnum(IncidentSeverity, name="incident_severity", create_type=False),
        default=IncidentSeverity.medium,
    )
    status = Column(
        SAEnum(IncidentStatus, name="incident_status", create_type=False),
        default=IncidentStatus.open,
    )
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    checkpoint_id = Column(Integer, ForeignKey("checkpoints.id"), nullable=True)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    cluster_size = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())