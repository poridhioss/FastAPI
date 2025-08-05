# Lab 5 - Combine SQL and NoSQL in One App

## 🎯 Lab Goals

- Build a FastAPI application that integrates **PostgreSQL (structured data)** and **MongoDB (unstructured data)**
- Demonstrate how SQL and NoSQL databases can **interoperate seamlessly in a single application**
- Implement JWT authentication with automatic session logging
- Create user profiles in PostgreSQL and activity logs in MongoDB
- Show cross-database validation and data consistency patterns
- Containerize the hybrid database application with Docker

## 📋 Deliverables

- ✅ PostgreSQL-backed user management with SQLAlchemy ORM
- ✅ MongoDB-backed activity logging with PyMongo
- ✅ JWT authentication with automatic session tracking
- ✅ `/users/{id}/logs` endpoint to fetch all logs for a given user
- ✅ `/logs/search?username={username}` endpoint for username-based log search
- ✅ Session logs created only on logout with calculated duration
- ✅ Cross-database validation ensuring data consistency
- ✅ Complete Docker containerization with multi-service setup
- ✅ Modular code structure demonstrating SQL/NoSQL integration patterns

## 🚀 Quick Start Guide

### Repository & Environment Setup

```bash
# Clone the repository
git clone clone https://github.com/poridhioss/FastAPI.git
cd FastAPI
cd lab05

### Container Setup

```bash
# Start PostgreSQL, MongoDB, and FastAPI services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Access Instructions

You can access the API by creating a load balancer. First, find the IP address of your lab:

```bash
ip addr show eth0
```

Then create a load balancer using this IP address and port 8000.
The load balancer's url will be something like 
`https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io`

The API will be available at:
- **API Base URL**: https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io
- **Interactive Docs**: https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/docs  
- **Alternative Docs**: https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/redoc

## 🔍 Understanding the Technologies

### **FastAPI Framework**
- Modern, fast web framework for building APIs with Python
- Automatic interactive documentation generation
- Built-in dependency injection system for authentication
- Type hints and Pydantic for request/response validation

### **PostgreSQL Database**
- Robust, open-source relational database for structured data
- ACID compliance ensuring user data integrity
- Advanced indexing for fast user lookups
- Perfect for normalized user profiles and authentication data

### **MongoDB Database**
- Document-oriented NoSQL database for flexible data storage
- Schema-less design ideal for varying log structures
- Powerful query and aggregation capabilities
- Horizontal scaling for high-volume activity logs

### **SQLAlchemy ORM**
- Python SQL toolkit for PostgreSQL operations
- Database abstraction with connection pooling
- Migration support for schema changes
- Session management for database transactions

### **PyMongo Driver**
- Official MongoDB driver for Python
- Direct document manipulation and queries
- Aggregation pipeline support for analytics
- Connection pooling and automatic failover

### **JWT (JSON Web Tokens)**
- Stateless authentication mechanism
- Self-contained tokens with user information
- Cryptographically signed for security
- Session tracking for activity logging

### **Passlib with bcrypt**
- Secure password hashing library
- bcrypt algorithm with salt generation
- Protection against rainbow table attacks
- Verification functions for login validation

## 🏗️ Project Structure

```
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application entry point
│   ├── database.py           # SQL & MongoDB connection setup
│   ├── models.py             # SQLAlchemy models (PostgreSQL)
│   ├── schemas.py            # Pydantic request/response schemas
│   └── auth.py               # Authentication utilities and JWT handling
├── requirements.txt          # Python dependencies
├── Dockerfile               # Application container configuration
├── docker-compose.yml       # Multi-service orchestration
├── .dockerignore            # Docker build exclusions
├── .gitignore               # Git exclusions
└── README.md                # This documentation
```

## Project Workflow
![Process Workflow](./assets/FastAPI%20Lab%205.drawio.svg)

## 🛠️ Implementation Details

### Key Models

#### PostgreSQL User Model
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### MongoDB Log Document Structure
```python
# Session log document in MongoDB
{
    "user_id": 1,
    "username": "madiha",
    "action": "session",
    "login_timestamp": "2024-01-01T10:00:00Z",
    "logout_timestamp": "2024-01-01T12:30:00Z",
    "session_duration": 9000,  # seconds
    "details": {
        "login_method": "username_password",
        "session_completed": true
    }
}
```

### Authentication & Session Flow

```python
# JWT token creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Session tracking (in-memory)
active_sessions = {
    "jwt_token": {
        "user_id": 1,
        "username": "madiha",
        "login_time": datetime.utcnow()
    }
}

# Cross-database validation
def create_log(user_id: int, log: LogCreate, db: Session):
    # Verify user exists in PostgreSQL
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Create log in MongoDB with PostgreSQL user data
    mongo_collection.insert_one({
        "user_id": user_id,
        "username": user.username,  # From PostgreSQL
        "action": log.action,
        "timestamp": datetime.utcnow()
    })
```

### Database Configuration

```python
# PostgreSQL setup with environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/userdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MongoDB setup with environment variables  
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGODB_URL)
mongo_db = mongo_client["activity_db"]
logs_collection = mongo_db["user_logs"]
```

## 📚 API Endpoints

### Health Check
- `GET /` - Root endpoint with API information
- `GET /health` - Service health status

### Authentication
- `POST /register` - User registration in PostgreSQL
- `POST /login` - User authentication and JWT token generation
- `POST /logout` - Session termination with MongoDB log creation

### User Management
- `GET /users/me` - Get current authenticated user profile
- `GET /users/{user_id}` - Get user by ID (PostgreSQL)

### Activity Logs
- `GET /users/{user_id}/logs` - Get all logs for specific user (MongoDB)
- `GET /logs/search?username={username}` - Search logs by username (MongoDB)
- `POST /users/{user_id}/logs` - Add custom activity log (MongoDB)
- `GET /logs/sessions` - Get all completed session logs (MongoDB)

### Request/Response Examples

#### User Registration
```bash
POST /register
Content-Type: application/json

{
  "username": "madiha",
  "email": "madiha@gmail.com",
  "password": "123"
}

# Response:
{
  "id": 1,
  "username": "madiha",
  "email": "madiha@example.com",
  "is_active": true
}
```

#### User Login (Session Start)
```bash
POST /login
Content-Type: application/json

{
  "username": "madiha",
  "password": "123"
}

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "madiha",
    "email": "madiha@gmail.com",
    "is_active": true
  }
}
```

#### User Logout (Session Log Creation)
```bash
POST /logout
Authorization: Bearer <jwt_token>

# Response:
{
  "message": "Successfully logged out. Session log created.",
  "session_duration": 9000,
  "login_time": "2024-01-01T10:00:00",
  "logout_time": "2024-01-01T12:30:00",
  "log_id": "507f1f77bcf86cd799439011"
}
```

#### Search User Logs by Username
```bash
GET /logs/search?username=madiha
Authorization: Bearer <jwt_token>

# Response:
[
  {
    "user_id": 1,
    "username": "madiha",
    "action": "session",
    "timestamp": "2024-01-01T10:00:00Z",
    "login_timestamp": "2024-01-01T10:00:00Z",
    "logout_timestamp": "2024-01-01T12:30:00Z",
    "session_duration": 9000,
    "details": {
      "login_method": "username_password",
      "session_completed": true
    }
  }
]
```

#### Get User Logs by ID
```bash
GET /users/1/logs
Authorization: Bearer <jwt_token>

# Response: Same format as search endpoint
```

## 🧪 Testing the API

### Testing using Postman

#### POST /register - User Registration
![User Registration](./assets/register_user.png)
---
#### POST /login - User Login
![User Login](./assets/login_user.png)
---
#### POST /logout - User Logout
![User Logout](./assets/logout.png)
---
#### GET /logs/search - Search User Logs
![User Search logs](./assets/log_search_username.png)
---
#### GET /users/{id}/logs - Get User Logs by ID
![User search logs by ID](./assets/users_useracc.png)
---
#### POST /users/{id}/logs - Post custom User Logs by ID
![User Post custom logs](./assets/user_log_creation_custom.png)
---
### Using FastAPI Interactive Docs

1. Navigate to `https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/docs`
2. Use the "Try it out" feature for each endpoint
3. For protected routes, click "Authorize" and enter `Bearer <your_token>`
4. Test the complete workflow: Register → Login → Add Logs → Search → Logout

### Testing with cURL

```bash
# Register user
curl -X POST "https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# Login and save token
TOKEN=$(curl -X POST "https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}' | jq -r '.access_token')

# Search logs by username
curl -H "Authorization: Bearer $TOKEN" \
  "https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/logs/search?username=testuser"

# Logout (creates session log)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/logout"
```

## 🔧 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check if containers are running
docker-compose ps

# View service logs
docker-compose logs postgres
docker-compose logs mongodb
docker-compose logs fastapi-app

# Restart services
docker-compose restart
```

**Cross-Database Validation Errors**
- Ensure user exists in PostgreSQL before creating MongoDB logs
- Check that both database connections are established
- Verify user_id consistency between databases

**Session Tracking Issues**
```bash
# Check active sessions (in application logs)
docker-compose logs fastapi-app | grep "active_sessions"

# Verify JWT token format
echo $TOKEN | cut -d'.' -f2 | base64 -d
```

**MongoDB Connection Issues**
```bash
# Connect to MongoDB container
docker-compose exec mongodb mongosh

# Check database and collection
use activity_db
db.user_logs.find({}).pretty()
```

**PostgreSQL Connection Issues**
```bash
# Connect to PostgreSQL container
docker-compose exec postgres psql -U postgres -d userdb

# Check users table
\dt
SELECT * FROM users;
```

### Docker Issues

```bash
# Rebuild all containers
docker-compose down
docker-compose up --build

# Remove volumes (caution: deletes all data)
docker-compose down -v

# Check individual service logs
docker-compose logs -f fastapi-app
docker-compose logs -f postgres
docker-compose logs -f mongodb

# Restart specific service
docker-compose restart fastapi-app
```

### Environment Variable Issues

```bash
# Check environment variables in container
docker-compose exec fastapi-app env | grep -E "(DATABASE_URL|MONGODB_URL)"

# Verify database URLs
echo $DATABASE_URL
echo $MONGODB_URL
```

## 🎯 Lab Completion Checklist

- [ ] PostgreSQL database running in Docker container
- [ ] MongoDB database running in Docker container  
- [ ] FastAPI application containerized and running
- [ ] User registration endpoint storing data in PostgreSQL
- [ ] User login endpoint generating JWT tokens
- [ ] Session tracking with in-memory storage
- [ ] User logout creating session logs in MongoDB
- [ ] Session duration calculation working correctly
- [ ] Cross-database validation ensuring data consistency
- [ ] Log search by username working in MongoDB
- [ ] Protected routes requiring JWT authentication
- [ ] Password hashing implemented with bcrypt
- [ ] Proper error handling for invalid requests
- [ ] Multi-service Docker setup working correctly
- [ ] API documentation accessible at `/docs`
- [ ] All endpoints tested and working correctly

## 🎓 Key Learning Outcomes

By completing this lab, you should understand:

- **Hybrid Database Architecture**: When and how to combine SQL and NoSQL databases
- **Data Modeling Decisions**: Choosing between structured and unstructured storage
- **Cross-Database Operations**: Maintaining consistency across different database types
- **Session Management**: Tracking user sessions across database boundaries
- **Authentication Integration**: JWT tokens with multi-database logging
- **Container Orchestration**: Managing multiple services with Docker Compose
- **API Design Patterns**: RESTful endpoints spanning multiple data stores
- **Query Optimization**: Efficient queries in both SQL and NoSQL contexts

## 🚧 Advanced Features (Optional Extensions)

### 1. **Advanced Log Analytics**
- Implement MongoDB aggregation pipelines for user activity analytics
- Add session duration statistics and user engagement metrics
- Create dashboard endpoints for activity insights

### 2. **Data Synchronization**
- Add event-driven synchronization between PostgreSQL and MongoDB
- Implement data consistency checks and repair mechanisms
- Add transaction-like behavior across databases

### 3. **Performance Optimization**
- Add connection pooling for both databases
- Implement caching layers (Redis) for frequently accessed data
- Add database indexing strategies for optimal query performance

### 4. **Advanced Search Features**
- Add full-text search capabilities in MongoDB
- Implement date range filtering and pagination
- Add real-time log streaming with WebSockets

### 5. **Data Migration Tools**
- Create scripts for migrating data between SQL and NoSQL
- Add backup and restore functionality for hybrid data
- Implement data archiving strategies

### 6. **Monitoring and Observability**
- Add application metrics for database operations
- Implement distributed tracing across database calls
- Add health checks for both database connections

### 7. **Security Enhancements**
- Add database-level encryption for sensitive logs
- Implement audit trails for cross-database operations
- Add role-based access control for different log types

### 8. **Scalability Features**
- Add MongoDB sharding for horizontal scaling
- Implement read replicas for PostgreSQL
- Add load balancing for database connections

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [JWT.io - JWT Debugger](https://jwt.io/)
- [Database Design Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/)

## 🔐 Security Best Practices

- Always use HTTPS in production environments
- Keep SECRET_KEY secure and rotate regularly
- Implement proper CORS policies for API access
- Use environment variables for sensitive database configurations
- Enable authentication for MongoDB in production
- Implement proper session timeout and cleanup
- Monitor database access patterns for suspicious activity
- Keep all dependencies updated for security patches
- Use SSL/TLS for database connections in production
- Implement proper input validation for all endpoints

## 🌟 Integration Patterns Demonstrated

### 1. **Cross-Database Validation**
- User existence verified in PostgreSQL before MongoDB operations
- Referential integrity maintained across database boundaries

### 2. **Hybrid Data Storage**
- Structured user data in PostgreSQL with ACID properties
- Flexible activity logs in MongoDB with schema evolution

### 3. **Session State Management**
- In-memory tracking bridging SQL and NoSQL operations
- Consistent user identification across both databases

### 4. **Unified API Interface**
- Single REST API exposing both SQL and NoSQL data
- Transparent database selection based on data type and use case 