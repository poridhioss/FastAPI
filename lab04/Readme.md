# Lab 4 - JWT Authentication with FastAPI and PostgreSQL

## 🎯 Lab Goals

- Implement user registration and login functionality
- Hash passwords securely using passlib with bcrypt
- Generate and validate JWT tokens for authentication
- Create protected routes using FastAPI's dependency injection
- Integrate PostgreSQL database with SQLAlchemy ORM
- Containerize the entire application with Docker

## 📋 Deliverables

- ✅ `/auth/signup` endpoint for user registration
- ✅ `/auth/login` endpoint for user authentication
- ✅ JWT access token generation and validation
- ✅ Protected route `/users/profile` accessible only with valid JWT
- ✅ Password hashing with bcrypt
- ✅ PostgreSQL database integration
- ✅ Complete Docker containerization
- ✅ Modular code structure with proper separation of concerns

## 🚀 Quick Start Guide

### Repository & Environment Setup

```bash
# Clone the repository
git clone https://github.com/poridhioss/FastAPI.git
cd lab04

# Create virtual environment (for local development)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Container Setup

```bash
# Start PostgreSQL and FastAPI services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Access Instructions

```bash
# Check your IP address (if running on cloud instance)
ip addr show eth0

```
```bash 
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
You can access the api by creating a load balancer for that you need to find out the ip address of your lab which you can check by writing 

```bash
ip addr show eth0
```
you then have to create a load balancer by using this ip address and port 8000

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc


## 🔍 Understanding the Technologies

### **FastAPI Framework**
- Modern, fast web framework for building APIs with Python
- Automatic interactive documentation generation
- Built-in dependency injection system
- Type hints and Pydantic for data validation

### **PostgreSQL Database**
- Robust, open-source relational database
- ACID compliance for data integrity
- Advanced indexing and query optimization
- JSON support for flexible data storage

### **SQLAlchemy ORM**
- Python SQL toolkit and Object-Relational Mapping library
- Database abstraction layer
- Migration support with Alembic
- Connection pooling and session management

### **JWT (JSON Web Tokens)**
- Stateless authentication mechanism
- Self-contained tokens with encoded user information
- Cryptographically signed for security
- Configurable expiration times

### **Passlib with bcrypt**
- Password hashing library
- bcrypt algorithm for secure password storage
- Salt generation for additional security
- Verification functions for authentication

## 🏗️ Project Structure

```
├── auth/
│   ├── utils.py              # Password hashing and JWT utilities
│   └── service.py            # User authentication business logic
├── middleware/
│   └── auth.py               # JWT authentication middleware
├── routes/
│   ├── auth.py               # Authentication endpoints
│   └── users.py              # Protected user endpoints
├── config.py                 # Application configuration
├── database.py               # Database connection and session management
├── models.py                 # SQLAlchemy database models
├── schemas.py                # Pydantic request/response schemas
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker services configuration
├── Dockerfile               # Container image configuration
└── README.md                # This documentation
```
## Project Workflow
![Process Workflow](./assets/Lab04.drawio.svg)

## 🛠️ Implementation Details

### Key Models

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

### Authentication Flow

```python
# Password hashing
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT token creation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

# Protected route dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = verify_token(token)
    return get_user_by_username(db, username)
```

### Configuration

```python
class Settings(BaseSettings):
    database_url: str = "postgresql://fastapi_user:fastapi_password@localhost:5432/jwt_auth_db"
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
```

## 📚 API Endpoints

### Health Check
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login and token generation

### Protected Routes
- `GET /users/profile` - Get current user profile (requires JWT)
- `GET /users/me` - Alternative endpoint for current user info

### Request/Response Examples

#### User Registration
```bash
POST /auth/signup
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### User Login
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepassword123"
}

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Protected Route Access
```bash
GET /users/profile
Authorization: Bearer <your_jwt_token>

# Response:
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z"
}
```

## 🧪 Testing the API


### Testing using postman

#### POST /auth/signup - User Registration
![User Registration](./assets/post_User.png)

**Endpoint**: `POST /auth/signup`

**Description**: Register a new user account

**Request**:
- **Method**: POST
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/auth/signup`
- **Content-Type**: `application/json`
- **Authentication**: None required

**Request Body**:
```json
{
  "username": "madiha",
  "email": "madiha@gmail.com",
  "password": "123"
}
```

**Response**:
- **Status**: 201 Created
- **Response Time**: 672ms
- **Response Size**: 950 B

**Response Body**:
```json
{
  "username": "madiha",
  "email": "madiha@gmail.com",
  "id": 1,
  "is_active": true,
  "created_at": "2025-07-15T17:15:22.385410Z",
  "updated_at": null
}
```

**Result**: ✅ Successfully created new user account

---

#### POST /auth/login - User Login
![User Login](./assets/login_user.png)

**Endpoint**: `POST /auth/login`

**Description**: Authenticate user and retrieve access token

**Request**:
- **Method**: POST
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/auth/login`
- **Content-Type**: `application/json`
- **Authentication**: None required

**Request Body**:
```json
{
  "username": "madiha",
  "password": "123"
}
```

**Response**:
- **Status**: 200 OK
- **Response Time**: 779ms
- **Response Size**: 1.01 KB

**Response Body**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYWRpaGEiLCJleHAiOjE3MjMxMDUzNTZ9.A_9YtqY0k4lxK8D8aM5ZGFdkVkbuDyCdkj-CSbU45Iw",
  "token_type": "bearer"
}
```

**Result**: ✅ Successfully authenticated user and returned access token

---


#### GET /users/profile - Get User Profile
![Get User Profile](./assets/get_User_Protected_route.png)

**Endpoint**: `GET /users/profile`

**Description**: Retrieve authenticated user's profile information

**Request**:
- **Method**: GET
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/users/profile`
- **Authentication**: Bearer Token Required
- **Headers**: `Authorization: Bearer <token>`

**Response**:
- **Status**: 200 OK
- **Response Time**: 467ms
- **Response Size**: 996 B

**Response Body**:
```json
{
  "username": "madiha",
  "email": "madiha@gmail.com",
  "id": 1,
  "is_active": true,
  "created_at": "2025-07-15T17:15:22.385410Z",
  "updated_at": null
}
```

**Result**: ✅ Successfully retrieves authenticated user profile

---

#### GET /users/me - Get Current User
![Get Current User](./assets/get_user_protected_route_alternative.png)

**Endpoint**: `GET /users/me`

**Description**: Retrieve current authenticated user information

**Request**:
- **Method**: GET
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/users/me`
- **Authentication**: Bearer Token Required
- **Headers**: `Authorization: Bearer <token>`

**Response**:
- **Status**: 200 OK
- **Response Time**: 370ms
- **Response Size**: 997 B

**Response Body**:
```json
{
  "username": "madiha",
  "email": "madiha@gmail.com",
  "id": 1,
  "is_active": true,
  "created_at": "2025-07-15T17:15:22.385410Z",
  "updated_at": null
}
```

**Result**: ✅ Successfully retrieves current user information

---


#### GET /health - Health Check
![Health Check](./assets/health_check.png)

**Endpoint**: `GET /health`

**Description**: Check API service health status

**Request**:
- **Method**: GET
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/health`
- **Authentication**: None required

**Response**:
- **Status**: 200 OK
- **Response Time**: 6ms
- **Response Size**: 145 B

**Response Body**:
```json
{
  "status": "healthy"
}
```

**Result**: ✅ API service is healthy and operational

---

### Using FastAPI Interactive Docs

1. Navigate to `https://67aba1ae1fcfb0b6f0fdce74-lb-307.bm-southeast.lab.poridhi.io/docs`
2. Use the "Try it out" feature for each endpoint
3. For protected routes, click "Authorize" and enter `Bearer <your_token>`

### Testing with Your IP Address

```bash
# Find your IP address
ip addr show eth0

```

## 🔧 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check if PostgreSQL container is running
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

**Token Validation Failed**
- Ensure token is properly formatted: `Bearer <token>`
- Check token expiration (default: 30 minutes)
- Verify SECRET_KEY is consistent

**Import Errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

**Port Already in Use**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

### Docker Issues

```bash
# Rebuild containers
docker-compose down
docker-compose up --build

# Remove volumes (caution: deletes data)
docker-compose down -v

# Check container logs
docker-compose logs api
docker-compose logs postgres
```

## 🎯 Lab Completion Checklist

- [ ] PostgreSQL database running in Docker container
- [ ] FastAPI application containerized and running
- [ ] User registration endpoint (`/auth/signup`) working
- [ ] User login endpoint (`/auth/login`) returning JWT tokens
- [ ] Password hashing implemented with bcrypt
- [ ] JWT token generation and validation working
- [ ] Protected route (`/users/profile`) accessible only with valid JWT
- [ ] Proper error handling for invalid credentials
- [ ] Modular code structure with separated concerns
- [ ] Docker-compose setup for easy deployment
- [ ] API documentation accessible at `/docs`
- [ ] All endpoints tested and working correctly

## 🎓 Key Learning Outcomes

By completing this lab, you should understand:

- **Authentication vs Authorization**: Difference between verifying identity and granting permissions
- **Password Security**: Why and how to hash passwords securely
- **JWT Tokens**: How stateless authentication works in modern applications
- **FastAPI Dependencies**: Using dependency injection for middleware and authentication
- **Database Integration**: Connecting FastAPI with PostgreSQL using SQLAlchemy
- **Docker Containerization**: Deploying applications with Docker and docker-compose
- **API Security**: Best practices for securing REST APIs
- **Modular Architecture**: Organizing code for maintainability and scalability

## 🚧 Advanced Features (Optional Extensions)

### 1. **Refresh Tokens**
- Implement refresh token mechanism for extended sessions
- Add token revocation functionality

### 2. **Role-Based Access Control (RBAC)**
- Add user roles and permissions
- Implement role-based route protection

### 3. **Rate Limiting**
- Add request rate limiting to prevent abuse
- Implement user-specific rate limits

### 4. **Email Verification**
- Add email verification for new registrations
- Implement password reset functionality

### 5. **Audit Logging**
- Log authentication attempts and user actions
- Add request/response logging middleware

### 6. **API Versioning**
- Implement API versioning strategy
- Add backward compatibility support

### 7. **Caching**
- Add Redis for session caching
- Implement user data caching

### 8. **Social Authentication**
- Add OAuth2 providers (Google, GitHub, etc.)
- Implement social login integration

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [JWT.io - JWT Debugger](https://jwt.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Passlib Documentation](https://passlib.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python-JOSE Documentation](https://python-jose.readthedocs.io/)

## 🔐 Security Best Practices

- Always use HTTPS in production
- Keep SECRET_KEY secure and rotate regularly
- Implement proper CORS policies
- Use environment variables for sensitive configuration
- Enable request validation and sanitization
- Monitor authentication attempts for suspicious activity
- Implement proper session management
- Keep dependencies updated for security patches