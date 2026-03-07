from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.database import Base


class CacheEntry(Base):
    __tablename__ = "cache_entries"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, nullable=False)
    cache_value = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
