from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """PostgreSQL User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# MongoDB document structure for logs:
# {
#   "user_id": int,
#   "username": str,
#   "action": str,  # "session" (created only on logout), "custom"
#   "login_timestamp": datetime,
#   "logout_timestamp": datetime,
#   "session_duration": int (in seconds, calculated from login to logout),
#   "details": dict (optional)
# }