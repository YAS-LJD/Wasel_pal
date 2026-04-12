from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func, Boolean
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id          = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    region      = Column(String(100), nullable=True)
    category    = Column(String(50), nullable=True)
    message     = Column(Text, nullable=False)
    created_at  = Column(DateTime, server_default=func.now())


class AlertSubscription(Base):
    __tablename__ = "alert_subscriptions"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    region     = Column(String(100), nullable=True)
    category   = Column(String(50), nullable=True)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())