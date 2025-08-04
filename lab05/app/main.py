from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from app.database import get_db, get_mongo, engine, Base
from app.models import User
from app.schemas import (
    UserCreate, User as UserSchema, UserLogin, Token, UserResponse,
    LogCreate, SessionLog, LogResponse
)
from app.auth import (
    get_password_hash, authenticate_user, create_access_token,
    decode_token, ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI SQL + NoSQL Demo with Authentication")
security = HTTPBearer()

# In-memory store for active sessions (in production, use Redis)
active_sessions = {}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@app.get("/")
def read_root():
    return {"message": "FastAPI + PostgreSQL + MongoDB Demo with Authentication"}

# Authentication endpoints
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active
    )

@app.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user - only stores session info, no log created yet"""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    login_time = datetime.utcnow()
    
    # Store session info for logout tracking (NO LOG CREATED YET)
    active_sessions[access_token] = {
        "user_id": user.id,
        "username": user.username,
        "login_time": login_time,
        "token_expires": login_time + access_token_expires
    }
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active
        )
    )

@app.post("/logout")
def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security), current_user: User = Depends(get_current_user)):
    """Logout user and CREATE session log with duration"""
    token = credentials.credentials
    
    if token not in active_sessions:
        raise HTTPException(status_code=400, detail="No active session found")
    
    session_info = active_sessions[token]
    logout_time = datetime.utcnow()
    login_time = session_info["login_time"]
    session_duration = int((logout_time - login_time).total_seconds())
    
    # CREATE the session log in MongoDB (only when user logs out)
    mongo_collection = get_mongo()
    session_log = {
        "user_id": session_info["user_id"],
        "username": session_info["username"],
        "action": "session",
        "login_timestamp": login_time,
        "logout_timestamp": logout_time,
        "session_duration": session_duration,
        "details": {
            "login_method": "username_password",
            "session_completed": True
        }
    }
    
    result = mongo_collection.insert_one(session_log)
    
    # Remove from active sessions
    del active_sessions[token]
    
    return {
        "message": f"Successfully logged out. Session log created.",
        "session_duration": session_duration,
        "login_time": login_time.isoformat(),
        "logout_time": logout_time.isoformat(),
        "log_id": str(result.inserted_id)
    }

# User endpoints
@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active
    )

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active
    )

# Log endpoints
@app.post("/users/{user_id}/logs")
def create_custom_log(
    user_id: int, 
    log: LogCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add custom activity log for user"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Save log to MongoDB
    mongo_collection = get_mongo()
    log_doc = {
        "user_id": user_id,
        "username": user.username,
        "action": log.action,
        "timestamp": datetime.utcnow(),
        "details": log.details
    }
    result = mongo_collection.insert_one(log_doc)
    
    return {"message": "Log created", "log_id": str(result.inserted_id)}

@app.get("/users/{user_id}/logs", response_model=List[LogResponse])
def get_user_logs_by_id(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all logs for a user by user ID"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get logs from MongoDB
    mongo_collection = get_mongo()
    logs = list(mongo_collection.find(
        {"user_id": user_id}, 
        {"_id": 0}
    ).sort("login_timestamp", -1).sort("timestamp", -1))
    
    # Format logs for response
    formatted_logs = []
    for log in logs:
        formatted_log = LogResponse(
            user_id=log["user_id"],
            username=log["username"],
            action=log["action"],
            timestamp=log.get("timestamp") or log.get("login_timestamp"),
            login_timestamp=log.get("login_timestamp"),
            logout_timestamp=log.get("logout_timestamp"),
            session_duration=log.get("session_duration"),
            details=log.get("details")
        )
        formatted_logs.append(formatted_log)
    
    return formatted_logs

@app.get("/logs/search", response_model=List[LogResponse])
def search_user_logs(
    username: str,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search logs by username and optionally filter by action"""
    # Verify user exists
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build MongoDB query
    query = {"username": username}
    if action:
        query["action"] = {"$regex": action, "$options": "i"}  # Case insensitive search
    
    # Get logs from MongoDB
    mongo_collection = get_mongo()
    logs = list(mongo_collection.find(
        query, 
        {"_id": 0}
    ).sort("login_timestamp", -1).sort("timestamp", -1))
    
    # Format logs for response
    formatted_logs = []
    for log in logs:
        formatted_log = LogResponse(
            user_id=log["user_id"],
            username=log["username"],
            action=log["action"],
            timestamp=log.get("timestamp") or log.get("login_timestamp"),
            login_timestamp=log.get("login_timestamp"),
            logout_timestamp=log.get("logout_timestamp"),
            session_duration=log.get("session_duration"),
            details=log.get("details")
        )
        formatted_logs.append(formatted_log)
    
    return formatted_logs

@app.get("/logs/sessions", response_model=List[LogResponse])
def get_all_login_sessions(current_user: User = Depends(get_current_user)):
    """Get all completed session logs"""
    mongo_collection = get_mongo()
    logs = list(mongo_collection.find(
        {"action": "session"}, 
        {"_id": 0}
    ).sort("login_timestamp", -1))
    
    # Format logs for response
    formatted_logs = []
    for log in logs:
        formatted_log = LogResponse(
            user_id=log["user_id"],
            username=log["username"],  
            action=log["action"],
            timestamp=log.get("login_timestamp"),
            login_timestamp=log.get("login_timestamp"),
            logout_timestamp=log.get("logout_timestamp"),
            session_duration=log.get("session_duration"),
            details=log.get("details")
        )
        formatted_logs.append(formatted_log)
    
    return formatted_logs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)