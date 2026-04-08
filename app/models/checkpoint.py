import enum

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base


class CheckpointStatus(str, enum.Enum):
    open       = "open"
    closed     = "closed"
    restricted = "restricted"
    unknown    = "unknown"


class CheckpointType(str, enum.Enum):
    military   = "military"
    commercial = "commercial"
    internal   = "internal"


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    name_ar     = Column(String(100), nullable=True)
    latitude    = Column(Numeric(9, 6), nullable=False)
    longitude   = Column(Numeric(9, 6), nullable=False)
    region      = Column(String(100), nullable=True)
    type        = Column(
        SAEnum(CheckpointType, name="checkpoint_type", create_type=False,
               values_callable=lambda x: [e.value for e in x]),
        default=CheckpointType.military,
    )
    status      = Column(
        SAEnum(CheckpointStatus, name="checkpoint_status", create_type=False,
               values_callable=lambda x: [e.value for e in x]),
        default=CheckpointStatus.open,
    )
    description = Column(Text, nullable=True)
    created_by  = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())

    status_history = relationship(
        "CheckpointStatusHistory", back_populates="checkpoint", lazy="dynamic"
    )


class CheckpointStatusHistory(Base):
    __tablename__ = "checkpoint_status_history"

    id            = Column(Integer, primary_key=True, index=True)
    checkpoint_id = Column(Integer, ForeignKey("checkpoints.id"), nullable=False)
    old_status    = Column(
        SAEnum(CheckpointStatus, name="checkpoint_status", create_type=False,
               values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    new_status    = Column(
        SAEnum(CheckpointStatus, name="checkpoint_status", create_type=False,
               values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    changed_by    = Column(Integer, ForeignKey("users.id"), nullable=True)
    reason        = Column(String(255), nullable=True)
    changed_at    = Column(DateTime, server_default=func.now())

    checkpoint = relationship("Checkpoint", back_populates="status_history")