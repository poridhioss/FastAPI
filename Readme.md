# FastAPI Learning Labs

A comprehensive collection of FastAPI labs designed to teach modern Python web API development from fundamentals to advanced concepts.

## 📋 Table of Contents

- [What is FastAPI?](#what-is-fastapi)
- [FastAPI vs Flask](#fastapi-vs-flask)
- [API Documentation](#api-documentation)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Labs Overview](#labs-overview)
- [Lab 01: FastAPI Fundamentals](#lab-01-fastapi-fundamentals)
- [Running the Labs](#running-the-labs)
- [Next Steps](#next-steps)

## What is FastAPI?

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. It's designed to be easy to use, fast to code, and production-ready.

### Key Features:
- **Fast**: Very high performance, on par with NodeJS and Go
- **Fast to code**: Increase development speed by 200-300%
- **Fewer bugs**: Reduce human-induced errors by 40%
- **Intuitive**: Great editor support with auto-completion
- **Easy**: Designed to be easy to use and learn
- **Short**: Minimize code duplication
- **Robust**: Get production-ready code with automatic interactive documentation
- **Standards-based**: Based on and fully compatible with OpenAPI and JSON Schema

## FastAPI vs Flask

| Feature | FastAPI | Flask |
|---------|---------|--------|
| **Performance** | Very High (async support) | Moderate |
| **Type Hints** | Built-in support | Manual implementation |
| **Data Validation** | Automatic with Pydantic | Manual with extensions |
| **Documentation** | Auto-generated (Swagger/ReDoc) | Manual setup required |
| **Async Support** | Native async/await | Limited (with extensions) |
| **Learning Curve** | Moderate | Easy |
| **API Standards** | OpenAPI 3.0 compliant | Manual implementation |
| **Request/Response** | Automatic serialization | Manual handling |

### When to Choose FastAPI:
- Building modern APIs with automatic documentation
- Need high performance and async support
- Want built-in data validation and serialization
- Prefer type safety and IDE support
- Building microservices or data-heavy applications
### What is uvicorn

Uvicorn is a lightning-fast ASGI (Asynchronous Server Gateway Interface) server designed to run asynchronous Python web applications. It’s the preferred server for frameworks like FastAPI that are built to handle asynchronous code efficiently.

#### Why Uvicorn with FastAPI?
FastAPI leverages Python’s async/await syntax to maximize concurrency and speed, especially when dealing with I/O-bound operations like database queries or external API calls. To run this async code properly, you need an ASGI server like Uvicorn, which can handle asynchronous event loops and concurrency seamlessly.

#### How is this different from Flask and Node.js?
Flask is synchronous and built on WSGI (Web Server Gateway Interface). It doesn’t require an ASGI server because it handles requests one at a time in a blocking manner. Running async code in Flask isn’t native or efficient.

Node.js is built on an asynchronous event-driven architecture by default, so it doesn’t need an extra server like Uvicorn. It’s designed to handle async operations natively.



## API Documentation

One of FastAPI's most powerful features is automatic API documentation generation:

### Interactive Documentation
Once your application is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
  - Interactive API documentation
  - Test endpoints directly in the browser
  - View request/response schemas
  - Generate code examples

- **ReDoc**: `http://localhost:8000/redoc`
  - Alternative documentation interface
  - Clean, professional appearance
  - Better for API reference documentation

### OpenAPI Schema
- **JSON Schema**: `http://localhost:8000/openapi.json`
  - Raw OpenAPI 3.0 specification
  - Use for generating client SDKs
  - Integration with API tools

### Documentation Features:
- Automatic schema generation from type hints
- Parameter descriptions and examples
- Response model documentation
- Error response documentation
- Authentication requirements
- Endpoint grouping and tagging


## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/madiha-ahmed-chowdhury/FastAPI.git
   cd FastAPI
   ```

2. **Navigate to any lab directory (e.g., lab01)**
   ```bash
   cd lab01
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate.bat
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

5. **Install required packages**
   ```bash
   pip install fastapi
   pip install uvicorn
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The `--reload` flag enables auto-reload during development, so the server restarts automatically when you make changes to your code.

## Project Structure

```
fastapi-labs/
├── README.md
├── lab01/
│   ├── app/
│   │   └── main.py
│   └── venv/
├── lab02/
│   ├── app/
│   │   └── main.py
│   └── venv/
├── lab03/
│   └── ...
├── ...
└── lab12/
    └── ...
```

## Labs Overview

| Lab | Topic | Key Concepts |
|-----|-------|--------------|
| **Lab 01** | FastAPI Fundamentals | Path parameters, Query parameters, Validation |


## Lab 01: FastAPI Fundamentals

The first lab introduces core FastAPI concepts through practical examples:

### Goals
 - Set up FastAPI project
 - Create a basic /ping health check endpoint
 - Learn path/query parameters

### FastAPI Path and Query Parameters Guide

#### Path Parameters

Path parameters are **required** parts of the URL path, defined with curly braces `{}`.

##### Single Path Parameter
```python
@app.get("/user/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```
**Usage**: `GET /user/5`

##### Multiple Path Parameters
```python
@app.get("/blogs/{blog_id}/comments/{comment_id}")
def get_comment(blog_id: int, comment_id: int):
    return {"blog_id": blog_id, "comment_id": comment_id}
```
**Usage**: `GET /blogs/10/comments/3`

##### Path Parameter Validation
```python
@app.get("/user/{user_id}")
def get_user(user_id: int = Path(..., gt=0, description="User ID must be positive")):
    return {"user_id": user_id}
```

#### Query Parameters

Query parameters appear after `?` in the URL and are separated by `&`.

##### Default Query Parameters
Parameters with default values can be **skipped** in the request:

```python
@app.get("/blog/all")
def get_blogs(page: int = Query(1), page_size: int = Query(10)):
    return {"page": page, "page_size": page_size}
```

**Usage**:
- `GET /blog/all` → uses defaults (page=1, page_size=10)
- `GET /blog/all?page=2` → page=2, page_size=10 (default)
- `GET /blog/all?page=2&page_size=20` → both specified

##### Optional Query Parameters
Optional parameters become `None` when not provided:

```python
@app.get("/blog/search")
def search_blogs(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    author: Optional[str] = Query(None)
):
    return {"q": q, "category": category, "author": author}
```

**Usage**:
- `GET /blog/search` → all parameters are `None`
- `GET /blog/search?q=python` → q="python", others are `None`
- `GET /blog/search?q=python&author=john` → q="python", author="john", category=`None`

##### Parameter Validation/Filters

FastAPI provides built-in validation for parameters:

###### Numeric Validation
```python
@app.get("/products/{product_id}")
def get_product(
    product_id: int = Path(..., ge=1, le=999999),  # Between 1 and 999999
    discount: float = Query(None, ge=0.0, le=100.0)  # 0% to 100%
):
    return {"product_id": product_id, "discount": discount}
```

###### String Validation
```python
@app.get("/test")
def test_params(
    name: str = Query(..., min_length=1, max_length=50),  # 1-50 characters
    email: str = Query(..., regex=r'^[^@]+@[^@]+\.[^@]+$')  # Email format
):
    return {"name": name, "email": email}
```

###### List Parameters
```python
@app.get("/search")
def search(tags: List[str] = Query([])):
    return {"tags": tags}
```
**Usage**: `GET /search?tags=python&tags=web&tags=api`

#### Combining Path and Query Parameters

```python
@app.get("/api/v1/users/{user_id}/posts/{post_id}")
def get_user_post(
    # Required path parameters
    user_id: int = Path(..., gt=0),
    post_id: int = Path(..., gt=0),
    
    # Optional query parameters with defaults
    include_comments: bool = Query(False),
    include_likes: bool = Query(False),
    format: str = Query("json")
):
    return {
        "user_id": user_id,
        "post_id": post_id,
        "include_comments": include_comments,
        "include_likes": include_likes,
        "format": format
    }
```

**Usage Examples**:
- `GET /api/v1/users/5/posts/12` → uses all defaults
- `GET /api/v1/users/5/posts/12?include_comments=true` → only comments included
- `GET /api/v1/users/5/posts/12?include_comments=true&include_likes=true&format=xml`

#### Key Differences

| Feature | Path Parameters | Query Parameters |
|---------|----------------|------------------|
| **Required** | Always required | Can be optional |
| **Position** | Fixed position in URL | After `?`, any order |
| **Default Values** | Not supported | Supported |
| **None Values** | Not applicable | Supported with Optional |
| **URL Structure** | `/users/{id}` | `/users?page=1&size=10` |

#### Common Validation Filters

- **Numeric**: `ge` (≥), `gt` (>), `le` (≤), `lt` (<)
- **String**: `min_length`, `max_length`, `regex`
- **General**: `description` for documentation

#### Best Practices

1. Use **path parameters** for resource identification (user ID, post ID)
2. Use **query parameters** for filtering, pagination, and optional features
3. Provide **default values** for commonly used query parameters
4. Use **Optional** for parameters that can be skipped
5. Add **validation** to ensure data integrity
6. Include **descriptions** for better API documentation

### Endpoints Covered:

#### Health Check
- **GET** `/ping` - Simple health check endpoint

#### Basic Greetings
- **GET** `/hello` - Basic greeting with default parameter
- **GET** `/hello/{name}` - Greeting with path parameter

#### Path Parameters
- **GET** `/blog/type/{type}` - Enum validation for blog types
- **GET** `/user/{user_id}` - Integer validation with constraints
- **GET** `/blogs/{blog_id}/comments/{comment_id}` - Multiple path parameters

#### Query Parameters
- **GET** `/blog/all` - Pagination with query parameters
- **GET** `/blog/search` - Multiple optional query filters
- **GET** `/api/v1/users/{user_id}/posts/{post_id}` - Complex parameter combinations

#### Validation Examples
- **GET** `/validate/email/{email}` - Email format validation with regex
- **GET** `/products/{product_id}` - Numeric validation and constraints
- **GET** `/test/parameters` - Comprehensive parameter type testing

### Key Learning Points:
- Path parameter validation using `Path()`
- Query parameter validation using `Query()`
- Enum validation for restricted values
- String validation with regex patterns
- Numeric constraints (ge, le, gt, lt)
- Optional parameters with default values
- List parameters for multiple values
- Combining path and query parameters

### FastAPI Endpoint Ordering Guide

Why endpoint ordering matters in FastAPI and how to do it correctly.

#### Why Ordering Matters

FastAPI matches routes **from top to bottom** using a **first-match wins** approach. Once it finds a matching pattern, it stops looking and executes that endpoint.

#### ❌ Wrong Order Example

```python
from fastapi import FastAPI

app = FastAPI()

# This general route comes first - PROBLEM!
@app.get("/users/{user_id}")
def get_user(user_id: str):
    return {"user_id": user_id}

# This will NEVER be reached because "me" matches {user_id}
@app.get("/users/me")
def get_current_user():
    return {"message": "Current user info"}
```

#### ✅ Correct Order Example

```python
from fastapi import FastAPI
from enum import Enum

app = FastAPI()

class ItemType(str, Enum):
    electronics = "electronics"
    books = "books"

# 1. Static/specific paths FIRST
@app.get("/users/me")
def get_current_user():
    return {"message": "Current user info"}

@app.get("/users/stats")
def get_user_stats():
    return {"message": "User statistics"}

# 2. Constrained parameters (enums) SECOND
@app.get("/items/category/{category}")
def get_items_by_category(category: ItemType):
    return {"category": category}

# 3. General parameters LAST
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```

#### Golden Rule

**Order your endpoints from MOST SPECIFIC to LEAST SPECIFIC:**

1. **Static paths** (e.g., `/users/me`, `/items/search`)
2. **Constrained parameters** (e.g., enums, specific types)
3. **General parameters** (e.g., `/{user_id}`, `/{item_id}`)

#### 🧪 Quick Test

If your ordering is correct:
- `/users/me` → hits the specific endpoint
- `/users/123` → hits the general `{user_id}` endpoint
- `/items/search` → hits search endpoint, not `{item_id}`

Remember: **Specific routes first, general routes last!**


### Testing Endpoints
#### API Testing Guide

##### Access Interactive Documentation

When your FastAPI server is running, go to:
```
http://localhost:8000/docs
```

##### Testing Endpoints
![Swagger UI](./assets/lab01_testingEndpoint_01.png)

###### Using the Interactive Docs
1. Find the endpoint you want to test
2. Click on it to expand
3. Click "Try it out"
4. Fill in the parameters (like in the screenshot: user_id=5, post_id=12)
5. Click "Execute"
6. View the response

###### Using cURL Commands
![Using terminal](./assets/lab01_testingEndpoint_terminal.png)

Copy the request URL from the docs and use it with cURL:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/users/6/posts/12?include_comments=true&include_likes=true&format=json' \
  -H 'accept: application/json'
```

###### Using Browser

For GET requests, copy the URL from the docs and paste directly into your browser:
```
http://127.0.0.1:8000/api/v1/users/5/posts/12?include_comments=true&include_likes=true&format=json
```

##### Quick Testing Steps

1. **Start your FastAPI server**
2. **Go to** `http://localhost:8000/docs`
3. **Find your endpoint** in the list
4. **Click and test** using the interface
5. **Copy the cURL command** if you need to use it elsewhere

The interactive docs automatically generate the correct URLs and show you exactly what your API returns.

## Lab 2 - PostgreSQL-Powered APIs with SQLAlchemy

### 🎯 Lab Goals
- Set up PostgreSQL with Docker
- Integrate SQLAlchemy ORM
- Create CRUD for a User table

### 📋 Deliverables
- User model with email/username fields
- /users endpoint with POST/GET/PUT/DELETE
- Use Alembic for migrations

---

### 🔍 Understanding the Technologies

#### PostgreSQL - The Database Engine

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

#### SQLAlchemy - The Object-Relational Mapper (ORM)

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

#### Alembic - Database Migration Manager

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

### 🏗️ How the System Works Together

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

#### Data Flow Explanation

1. **Client Request**: A user sends an HTTP request (GET, POST, PUT, DELETE) to our API
2. **FastAPI Routing**: FastAPI receives the request and routes it to the appropriate endpoint function
3. **Data Validation**: Pydantic schemas validate the incoming data format
4. **ORM Translation**: SQLAlchemy converts Python objects to SQL queries
5. **Database Operation**: PostgreSQL executes the SQL and returns results
6. **Response Formation**: Data flows back through the layers and is returned as JSON

#### Example: Creating a User

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

### 🛠️ Step-by-Step Implementation

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

#### Step 2: Database Connection with SQLAlchemy

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

#### Step 3: Creating the User Model

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

#### Step 4: Data Validation with Pydantic Schemas

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

#### Step 5: CRUD Operations

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

#### Step 6: FastAPI Endpoints

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

#### Step 7: Database Migrations with Alembic

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

### 🔄 Complete System Workflow

#### 1. Development Process

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

#### 2. Request/Response Cycle

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

#### 3. Error Handling Flow

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

### 🎯 Lab Completion Checklist

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

### 🎓 Key Learning Outcomes

By completing this lab, we will understand:

1. **Database Design**: How to structure relational data with proper constraints
2. **ORM Concepts**: Object-relational mapping and its benefits
3. **API Development**: RESTful API principles and implementation
4. **Database Migrations**: Version control for database schemas
5. **Data Validation**: Input validation and error handling
6. **Docker**: Containerization for development environments
7. **System Integration**: How different components work together

This lab provides a solid foundation for building scalable, maintainable web applications with proper database management and API design patterns.
## Running the Labs
### FastAPI Development Setup Guide

#### Windows Setup for VS Code Terminal

**Important**: For Windows users working with multiline commands in VS Code, you'll need to configure Git Bash as your default terminal.

##### VS Code Terminal Configuration

Add this to your VS Code `settings.json`:

```json
{
  "terminal.integrated.profiles.windows": {
    "Git Bash": {
      "path": "C:\\Program Files\\Git\\bin\\bash.exe"
    }
  },
  "terminal.integrated.defaultProfile.windows": "Git Bash"
}
```

**Prerequisites**: 
- Install Git for Windows (includes Git Bash)
- This enables proper handling of Unix-style commands and multiline scripts

### Development Commands

#### Development Mode
```bash
# Navigate to any lab directory
cd lab01

# Activate virtual environment
venv\Scripts\activate.bat  # Windows Command Prompt
# or
source venv/bin/activate   # Git Bash/macOS/Linux

# Run with auto-reload
uvicorn app.main:app --reload
```

### Production Mode
```bash
# Run without reload for better performance
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Custom Configuration
```bash
# Run on different host/port
uvicorn app.main:app --host 127.0.0.1 --port 3000 --reload

# Run with specific log level
uvicorn app.main:app --log-level debug
```
