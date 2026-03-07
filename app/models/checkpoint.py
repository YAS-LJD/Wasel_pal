from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.database import Base


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(40), default="open")
    created_at = Column(DateTime, server_default=func.now())
