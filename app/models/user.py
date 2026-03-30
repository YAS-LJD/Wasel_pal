from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    citizen   = "citizen"
    moderator = "moderator"
    admin     = "admin"

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50), unique=True, nullable=False)
    email         = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role          = Column(SAEnum(UserRole, name="user_role", create_type=False), default=UserRole.citizen)
    reputation    = Column(Float, default=1.0)
    total_reports = Column(Integer, default=0)
    valid_reports = Column(Integer, default=0)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(TIMESTAMP, server_default=func.now())
    updated_at    = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())