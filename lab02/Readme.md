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

## 🚀 Quick Start Guide

### Step 1: Clone the Repository and Setup Environment

```bash
# Clone the repository
git clone https://github.com/madiha-ahmed-chowdhury/FastAPI.git
cd FastAPI/lab02

# Update system & install Python if needed
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# Check Python and pip versions
python3 --version
pip3 --version

# Upgrade pip (optional but recommended)
python3 -m pip install --upgrade pip

# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies if requirements.txt is present
pip install -r requirements.txt
```

### Step 2: Environment Configuration
Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add the following content to `.env`:
```env
# Database Configuration
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/mydb

# PostgreSQL Credentials
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydb
```

### Step 3: Docker Setup for PostgreSQL
Start PostgreSQL:
```bash
docker-compose up -d
```

### Step 4: Initialize and Configure Alembic
```bash
# Initialize Alembic
alembic init alembic
```

Replace the content of `alembic/env.py` with:

```python
from logging.config import fileConfig
import os
from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Load environment variables
load_dotenv()

# Import your models
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.models import Base

# this is the Alembic Config object
config = context.config

# Set the database URL from environment
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Step 5: Create and Apply Migrations
```bash
# Create initial migration
alembic revision --autogenerate -m "Create users table"

# Apply migration
alembic upgrade head
```

### Step 6: Start the Application
```bash
# Start FastAPI server
uvicorn app.main:app --reload
```

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

### Alembic - Database Migration Manager

**Alembic** is SQLAlchemy's database migration tool. It manages changes to your database schema over time.

**What are Database Migrations?**
Migrations are version-controlled changes to your database structure. They allow you to:
- **Track Changes**: Every modification to your database schema is recorded
- **Apply Updates**: Safely update database structure in development, staging, and production
- **Rollback**: Undo changes if something goes wrong
- **Collaborate**: Team members get the same database structure

---

## 🏗️ Project Structure

```
lab02/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── database.py      # Database configuration
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── crud.py          # Database operations
├── alembic/
│   ├── versions/        # Migration files
│   └── env.py          # Alembic configuration
├── .env                # Environment variables
├── docker-compose.yml  # PostgreSQL container
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

---

## 🛠️ Implementation Details

### Database Configuration (app/database.py)
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### User Model (app/models.py)
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Pydantic Schemas (app/schemas.py)
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

---

## 🧪 Testing Commands

### API Testing with curl
```bash
# Create user
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","username":"johndoe"}'

# Get all users
curl -X GET http://localhost:8000/users/

# Get specific user
curl -X GET http://localhost:8000/users/1

# Update user
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email":"john.updated@example.com"}'

# Delete user
curl -X DELETE http://localhost:8000/users/1
```

### Database Operations
```bash
# Check PostgreSQL container status
docker ps

# Connect to PostgreSQL
docker exec -it postgres_db psql -U myuser -d mydb

# SQL commands inside PostgreSQL
\dt                    # List tables
SELECT * FROM users;   # Query users
\q                     # Quit
```

### Migration Commands
```bash
# Check current migration status
alembic current

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check if PostgreSQL is running
   docker ps
   
   # Restart PostgreSQL
   docker-compose down
   docker-compose up -d
   ```

2. **Migration Errors**
   ```bash
   # Reset migrations (careful - this deletes data!)
   alembic downgrade base
   alembic upgrade head
   ```

3. **Port Already in Use**
   ```bash
   # Check what's using port 5432
   sudo lsof -i :5432
   
   # Kill the process or use different port in docker-compose.yml
   ```

4. **Virtual Environment Issues**
   ```bash
   # Deactivate and recreate virtual environment
   deactivate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## 🎯 Lab Completion Checklist

✅ **Environment Setup**
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] .env file configured

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

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)

---