from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# User schemas (PostgreSQL)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Log schemas (MongoDB)
class LogCreate(BaseModel):
    action: str
    details: Optional[Dict[str, Any]] = None

class SessionLog(BaseModel):
    user_id: int
    username: str
    action: str
    login_timestamp: datetime
    logout_timestamp: Optional[datetime] = None
    session_duration: Optional[int] = None  # in seconds
    details: Optional[Dict[str, Any]] = None

class LogResponse(BaseModel):
    user_id: int
    username: str
    action: str
    timestamp: datetime
    login_timestamp: Optional[datetime] = None
    logout_timestamp: Optional[datetime] = None
    session_duration: Optional[int] = None
    details: Optional[Dict[str, Any]] = None