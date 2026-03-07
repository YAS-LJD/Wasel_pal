from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(80), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(40), default="pending")
    created_at = Column(DateTime, server_default=func.now())
