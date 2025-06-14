# Lab 2 - PostgreSQL-Powered APIs with SQLAlchemy

## 🎯 Lab Goals
- Set up PostgreSQL with Docker
- Integrate SQLAlchemy ORM
- Create CRUD for a User table

## 📋 Deliverables
- User model with email/username fields
- /users endpoint with POST/GET/PUT/DELETE
- Use Alembic for migrations

---

## 🔍 Understanding the Technologies

### PostgreSQL - The Database Engine

**PostgreSQL** is a powerful, open-source relational database management system (RDBMS). Think of it as a highly organized filing cabinet that can store, retrieve, and manage vast amounts of data efficiently.

**Key Features:**
- **ACID Compliance**: Ensures data integrity through Atomicity, Consistency, Isolation, and Durability
- **Relational Structure**: Data is organized in tables with relationships between them
- **SQL Support**: Uses Structured Query Language for data operations
- **Concurrent Access**: Multiple applications can safely access the database simultaneously
- **Scalability**: Handles everything from small applications to enterprise-level systems

**Why PostgreSQL for this lab?**
- Robust and reliable for production applications
- Excellent Python integration
- Strong community support
- Advanced features like JSON support, full-text search, and custom data types

### SQLAlchemy - The Object-Relational Mapper (ORM)

**SQLAlchemy** is a Python toolkit that provides a high-level interface for working with databases. Instead of writing raw SQL queries, you work with Python objects and classes.

**What is an ORM?**
An ORM (Object-Relational Mapper) bridges the gap between object-oriented programming and relational databases. It translates between:
- **Python objects** ↔ **Database tables**
- **Object attributes** ↔ **Table columns**
- **Object methods** ↔ **SQL operations**

**Example of ORM Magic:**
```python
# Without ORM (Raw SQL):
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
result = cursor.fetchone()

# With SQLAlchemy ORM:
user = db.query(User).filter(User.email == email).first()
```

**SQLAlchemy Benefits:**
- **Database Abstraction**: Switch between PostgreSQL, MySQL, SQLite with minimal code changes
- **Type Safety**: Python type hints catch errors before runtime
- **Relationship Management**: Easily define and work with table relationships
- **Query Building**: Construct complex queries using Python syntax
- **Connection Management**: Automatic connection pooling and session handling

### Alembic - Database Migration Manager

**Alembic** is SQLAlchemy's database migration tool. It manages changes to your database schema over time.

**What are Database Migrations?**
Migrations are version-controlled changes to your database structure. They allow you to:
- **Track Changes**: Every modification to your database schema is recorded
- **Apply Updates**: Safely update database structure in development, staging, and production
- **Rollback**: Undo changes if something goes wrong
- **Collaborate**: Team members get the same database structure

**Migration Workflow:**
1. **Change Model**: Modify your SQLAlchemy model
2. **Generate Migration**: Alembic creates a migration script
3. **Review Script**: Check the generated SQL commands
4. **Apply Migration**: Execute the changes on your database

**Example Migration Process:**
```python
# 1. Add new field to model
class User(Base):
    # ... existing fields ...
    phone = Column(String(20))  # NEW FIELD

# 2. Generate migration
alembic revision --autogenerate -m "Add phone field to users"

# 3. Apply migration
alembic upgrade head
```

---

## 🏗️ How the System Works Together

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTTP Client   │    │   FastAPI       │    │   PostgreSQL    │
│  (Browser/App)  │◄──►│   Application   │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
    JSON Requests          Python Objects        SQL Queries
    JSON Responses         SQLAlchemy ORM       Table Records
```

### Data Flow Explanation

1. **Client Request**: A user sends an HTTP request (GET, POST, PUT, DELETE) to our API
2. **FastAPI Routing**: FastAPI receives the request and routes it to the appropriate endpoint function
3. **Data Validation**: Pydantic schemas validate the incoming data format
4. **ORM Translation**: SQLAlchemy converts Python objects to SQL queries
5. **Database Operation**: PostgreSQL executes the SQL and returns results
6. **Response Formation**: Data flows back through the layers and is returned as JSON

### Example: Creating a User

```python
# 1. HTTP Request comes in
POST /users/
{
  "email": "john@example.com",
  "username": "johndoe"
}

# 2. FastAPI endpoint receives request
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

# 3. Pydantic validates data
UserCreate(email="john@example.com", username="johndoe")

# 4. SQLAlchemy creates database object
db_user = User(email=user.email, username=user.username)

# 5. Database operation
db.add(db_user)
db.commit()

# 6. PostgreSQL executes:
INSERT INTO users (email, username, is_active, created_at) 
VALUES ('john@example.com', 'johndoe', true, NOW())
```

---

## 🛠️ Step-by-Step Implementation

### Step 1: Setting Up PostgreSQL with Docker

**Why Docker?**
Docker containerizes PostgreSQL, making it easy to:
- Install consistently across different systems
- Isolate database from host system
- Manage database lifecycle (start, stop, restart)
- Ensure same version across team members

**Docker Compose Configuration:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15                    # PostgreSQL version 15
    container_name: postgres_db           # Container name for easy reference
    environment:
      POSTGRES_USER: myuser              # Database username
      POSTGRES_PASSWORD: mypassword      # Database password
      POSTGRES_DB: mydb                  # Initial database name
    ports:
      - "5432:5432"                      # Map container port to host port
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persist data between restarts
    restart: unless-stopped              # Auto-restart container

volumes:
  postgres_data:                         # Named volume for data persistence
```

**How this works:**
- **Image**: Downloads PostgreSQL 15 from Docker Hub
- **Environment Variables**: Configure database credentials
- **Port Mapping**: Makes database accessible on localhost:5432
- **Volume**: Ensures data survives container restarts
- **Restart Policy**: Automatically restarts if container crashes

### Step 2: Database Connection with SQLAlchemy

**Database Configuration:**

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
# Example: "postgresql://myuser:mypassword@localhost:5432/mydb"

# Create database engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency injection for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db        # Provide database session to endpoint
    finally:
        db.close()      # Ensure session is closed after use
```

**Configuration Breakdown:**
- **Engine**: The core interface to the database
- **SessionLocal**: Factory for creating database sessions
- **Base**: Base class that all models inherit from
- **get_db()**: Dependency injection function for FastAPI

### Step 3: Creating the User Model

**User Model Definition:**

```python
# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"               # Table name in PostgreSQL
    
    # Primary key - auto-incrementing integer
    id = Column(Integer, primary_key=True, index=True)
    
    # Email field - unique and indexed for fast lookups
    email = Column(String, unique=True, index=True, nullable=False)
    
    # Username field - unique and indexed
    username = Column(String, unique=True, index=True, nullable=False)
    
    # Active status - boolean with default True
    is_active = Column(Boolean, default=True)
    
    # Timestamp fields - automatically managed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Model Explanation:**
- **`__tablename__`**: Specifies the PostgreSQL table name
- **Columns**: Define the structure and constraints
- **Indexes**: Speed up queries on email and username
- **Constraints**: `unique=True` prevents duplicate emails/usernames
- **Timestamps**: Automatically track when records are created/updated

**What happens in PostgreSQL:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_username ON users (username);
```

### Step 4: Data Validation with Pydantic Schemas

**Schema Definitions:**

```python
# app/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base schema with common fields
class UserBase(BaseModel):
    email: EmailStr      # Validates email format
    username: str        # String field

# Schema for creating users (inherits from UserBase)
class UserCreate(UserBase):
    pass                 # No additional fields needed

# Schema for updating users (all fields optional)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None

# Schema for returning user data (includes all fields)
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True    # Allow ORM object conversion
```

**Schema Purpose:**
- **UserCreate**: Validates data when creating new users
- **UserUpdate**: Validates partial updates (optional fields)
- **User**: Defines the structure of API responses
- **EmailStr**: Ensures email addresses are properly formatted

### Step 5: CRUD Operations

**Database Operations:**

```python
# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional

# READ operations
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get all users with pagination"""
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Check if email already exists"""
    return db.query(models.User).filter(models.User.email == email).first()

# CREATE operation
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create new user"""
    db_user = models.User(email=user.email, username=user.username)
    db.add(db_user)      # Add to session
    db.commit()          # Save to database
    db.refresh(db_user)  # Refresh with database-generated values
    return db_user

# UPDATE operation
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update existing user"""
    db_user = get_user(db, user_id)
    if db_user:
        # Update only provided fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# DELETE operation
def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
```

**CRUD Explanation:**
- **Session Management**: Each function receives a database session
- **Query Building**: Uses SQLAlchemy's query interface
- **Error Handling**: Returns None/False when records don't exist
- **Transactions**: commit() saves changes, rollback() undoes them

### Step 6: FastAPI Endpoints

**API Implementation:**

```python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas
from .database import engine, get_db

# Create database tables (development only)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API", version="1.0.0")

# CREATE - POST /users/
@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check for duplicate email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    return crud.create_user(db=db, user=user)

# READ - GET /users/
@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# READ - GET /users/{user_id}
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# UPDATE - PUT /users/{user_id}
@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update user"""
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# DELETE - DELETE /users/{user_id}
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
```

**Endpoint Breakdown:**
- **Dependency Injection**: `Depends(get_db)` provides database session
- **Response Models**: Pydantic schemas define response structure
- **Error Handling**: HTTPException for client errors
- **Status Codes**: Appropriate HTTP status codes for each operation

### Step 7: Database Migrations with Alembic

**Alembic Configuration:**

```ini
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = # Will be set from environment variables

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic
```

**Environment Configuration:**

```python
# alembic/env.py
from logging.config import fileConfig
import os
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context

# Load environment variables
load_dotenv()

# Import models for autogeneration
from app.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

**Migration Workflow:**

1. **Initialize Alembic:**
   ```bash
   alembic init alembic
   ```

2. **Create Migration:**
   ```bash
   alembic revision --autogenerate -m "Create users table"
   ```

3. **Apply Migration:**
   ```bash
   alembic upgrade head
   ```

**What Alembic Does:**
- **Compares**: Current database schema vs. model definitions
- **Generates**: SQL commands to update the database
- **Tracks**: Which migrations have been applied
- **Rollback**: Can undo migrations if needed

---

## 🔄 Complete System Workflow

### 1. Development Process

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Create/modify models
# Edit app/models.py

# 3. Generate migration
alembic revision --autogenerate -m "Description"

# 4. Apply migration
alembic upgrade head

# 5. Start API server
uvicorn app.main:app --reload

# 6. Test endpoints
curl -X POST http://localhost:8000/users/ -d '{"email":"test@example.com","username":"testuser"}'
```

### 2. Request/Response Cycle

```python
# Client sends request
POST /users/
{
  "email": "john@example.com",
  "username": "johndoe"
}

# FastAPI processes request
↓
# Pydantic validates data
UserCreate(email="john@example.com", username="johndoe")
↓
# CRUD function called
crud.create_user(db, user)
↓
# SQLAlchemy generates SQL
INSERT INTO users (email, username, is_active, created_at) 
VALUES ('john@example.com', 'johndoe', true, NOW()) 
RETURNING id, email, username, is_active, created_at, updated_at
↓
# PostgreSQL executes query
Returns: (1, 'john@example.com', 'johndoe', true, '2025-06-15 10:30:00', null)
↓
# Response sent to client
{
  "id": 1,
  "email": "john@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2025-06-15T10:30:00.123456",
  "updated_at": null
}
```

### 3. Error Handling Flow

```python
# Client sends invalid data
POST /users/
{
  "email": "invalid-email",
  "username": "johndoe"
}

# Pydantic validation fails
↓
# FastAPI returns 422 Unprocessable Entity
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## 🎯 Lab Completion Checklist

✅ **PostgreSQL Setup**
- [ ] Docker Compose file created
- [ ] PostgreSQL container running on port 5432
- [ ] Database accessible from Python application

✅ **SQLAlchemy Integration**
- [ ] Database connection established
- [ ] Base model class created
- [ ] Session management implemented

✅ **User Model**
- [ ] User class with email and username fields
- [ ] Proper constraints (unique, not null)
- [ ] Timestamp fields for created_at and updated_at

✅ **CRUD Operations**
- [ ] Create user function
- [ ] Read user(s) functions
- [ ] Update user function
- [ ] Delete user function

✅ **API Endpoints**
- [ ] POST /users/ - Create user
- [ ] GET /users/ - List users
- [ ] GET /users/{id} - Get specific user
- [ ] PUT /users/{id} - Update user
- [ ] DELETE /users/{id} - Delete user

✅ **Alembic Migrations**
- [ ] Alembic initialized
- [ ] Initial migration created
- [ ] Migration applied to database
- [ ] Database schema matches models

✅ **Testing**
- [ ] All endpoints tested with valid data
- [ ] Error handling tested
- [ ] Database operations verified

---

## 🎓 Key Learning Outcomes

By completing this lab, you will understand:

1. **Database Design**: How to structure relational data with proper constraints
2. **ORM Concepts**: Object-relational mapping and its benefits
3. **API Development**: RESTful API principles and implementation
4. **Database Migrations**: Version control for database schemas
5. **Data Validation**: Input validation and error handling
6. **Docker**: Containerization for development environments
7. **System Integration**: How different components work together

This lab provides a solid foundation for building scalable, maintainable web applications with proper database management and API design patterns.