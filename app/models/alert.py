from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(255), nullable=False)
    level = Column(String(20), default="info")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
