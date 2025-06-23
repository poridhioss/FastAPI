# Lab 3 - MongoDB-Powered Notes API with FastAPI

## 🎯 Lab Goals
- Set up MongoDB with Docker
- Build a FastAPI application with async operations
- Create CRUD operations for a Notes management system
- Implement search functionality

## 📋 Deliverables
- Note model with title, content, and tags fields
- /notes endpoint with POST/GET/PUT/DELETE operations
- Search functionality for notes
- MongoDB integration with sample data

---

## 🚀 Quick Start Guide

### Step 1: Clone the Repository and Setup Environment

```bash
# Clone the repository
git clone https://github.com/madiha-ahmed-chowdhury/FastAPI.git
cd notes-api

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

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Docker Setup for MongoDB

Start MongoDB and Mongo Express:
```bash
# Start MongoDB container
docker-compose up -d

# Verify containers are running
docker ps
```

This will start:
- **MongoDB** on port `27017`
- **Mongo Express** (web UI) on port `8081`

### Step 3: Verify Database Setup

Access Mongo Express web interface by creating a load balancer for that you need to find out the ip address of your lab which you can check by writing 
```
bash
ip addr show eth0
```
you then have to create a load balancer by using this ip address and port 8001

Login credentials:
- Username: `admin`
- Password: `admin`

You should see the `notesdb` database with sample notes already created.

### Step 4: Start the FastAPI Application

```bash
# Start the API server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
You can access the api by creating a load balancer for that you need to find out the ip address of your lab which you can check by writing 
```
bash
ip addr show eth0
```
you then have to create a load balancer by using this ip address and port 8000

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 🔍 Understanding the Technologies

### MongoDB - The NoSQL Database

**MongoDB** is a document-oriented NoSQL database that stores data in flexible, JSON-like documents called BSON (Binary JSON).

**Key Features:**
- **Document Storage**: Data stored as documents, not rows and tables
- **Flexible Schema**: No predefined structure, documents can have different fields
- **Horizontal Scaling**: Easy to scale across multiple servers
- **Rich Query Language**: Powerful querying and indexing capabilities
- **JSON-like Documents**: Natural fit for web applications

**Why MongoDB for this lab?**
- Perfect for rapid prototyping with flexible data structures
- Excellent Python integration with Motor (async driver)
- Built-in support for complex data types like arrays
- No need for complex migrations when adding new fields

### FastAPI - Modern Python Web Framework

**FastAPI** is a modern, high-performance web framework for building APIs with Python 3.6+ based on standard Python type hints.

**Key Features:**
- **Async Support**: Built for high-performance async operations
- **Automatic Documentation**: Interactive API docs generated automatically
- **Type Safety**: Built-in validation using Python type hints
- **Fast Performance**: One of the fastest Python frameworks
- **Easy to Use**: Simple and intuitive API design

### Motor - Async MongoDB Driver

**Motor** is the recommended async Python driver for MongoDB, designed to work with asyncio and modern Python async/await syntax.

**Benefits:**
- **Non-blocking Operations**: Database operations don't block the event loop
- **High Concurrency**: Handle many requests simultaneously
- **Better Performance**: Especially important for I/O intensive applications

---

## 🏗️ Project Structure

```
notes-api/
├── main.py                 # FastAPI application
├── docker-compose.yml      # MongoDB container setup
├── init-mongo.js          # Database initialization script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🛠️ Implementation Details

### Note Data Model

```python
class NoteModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = []
```

**Fields:**
- **id**: MongoDB ObjectId (auto-generated)
- **title**: Note title (1-100 characters, required)
- **content**: Note content (required, any length)
- **tags**: Optional list of string tags for categorization

### Database Configuration

```python
# MongoDB connection with authentication
client = AsyncIOMotorClient("mongodb://admin:password123@localhost:27017/?authSource=admin")
database = client.notesdb
notes_collection = database.notes
```

### Application Lifecycle Management

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await connect_to_mongo()
    yield
    # Shutdown: Close MongoDB connection
    await close_mongo_connection()
```

---

## 📚 API Endpoints

### 1. Health Check
- **GET /** - Check if API is running
- **Response**: `{"message": "Notes API is running!", "status": "healthy"}`

### 2. Notes Management

#### Create Note
- **POST /notes**
- **Body**: `{"title": "string", "content": "string", "tags": ["string"]}`
- **Response**: Created note with auto-generated ID

#### Get All Notes
- **GET /notes**
- **Response**: Array of all notes

#### Get Specific Note
- **GET /notes/{note_id}**
- **Response**: Single note or 404 if not found

#### Update Note
- **PUT /notes/{note_id}**
- **Body**: `{"title": "string", "content": "string", "tags": ["string"]}`
- **Response**: Updated note or 404 if not found

#### Delete Note
- **DELETE /notes/{note_id}**
- **Response**: Success message or 404 if not found

### 3. Search Functionality

#### Search Notes
- **GET /notes/search/{query}**
- **Description**: Search in title, content, and tags
- **Example**: `/notes/search/welcome`
- **Response**: Array of matching notes

---

## 🧪 Testing the API

### Using curl Commands

```bash
# Health check
curl -X GET http://localhost:8000/

# Get all notes
curl -X GET http://localhost:8000/notes

# Create a new note
curl -X POST http://localhost:8000/notes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Note",
    "content": "This is the content of my first note",
    "tags": ["personal", "todo"]
  }'

# Get specific note (replace {id} with actual note ID)
curl -X GET http://localhost:8000/notes/{note_id}

# Update a note
curl -X PUT http://localhost:8000/notes/{note_id} \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Note Title",
    "content": "Updated content",
    "tags": ["updated", "important"]
  }'

# Search notes
curl -X GET http://localhost:8000/notes/search/welcome

# Delete a note
curl -X DELETE http://localhost:8000/notes/{note_id}
```

### Using FastAPI Interactive Docs

1. Open http://localhost:8000/docs in your browser
2. Explore and test all endpoints interactively
3. View request/response schemas and examples

### Using MongoDB Compass or Mongo Express

1. **Mongo Express**: http://localhost:8081 (admin/admin)
2. **MongoDB Compass**: Connect to `mongodb://admin:password123@localhost:27017/?authSource=admin`

---
## Testing Using Postman

## Overview
After deploying the Notes API in the lab environment, we can thoroughly test all endpoints using Postman.
For this we need to create a load balancer first, for creating a load balamcer we need to find out the ip address of our virtual machine, we can find it by writing the below code in the terminal
```bash
ip addr show eth0
```
This will give us a ip address like 10.13.12.133/16 we need to take 10.13.12.133 part and fill it in the ip address section in the load balancer. For the port section in the load balancer we need to use 8000 as we deployed the api in 8000 port. It will give us a load balancer like `https://67aba1ae1fcfb0b6f0fdce74-lb-934.bm-southeast.lab.poridhi.io`
As we are using users/ endpoint we need to add this to the load balancer url and then the API is accessible at `https://67aba1ae1fcfb0b6f0fdce74-lb-934.bm-southeast.lab.poridhi.io/notes`. for y

## API Endpoints Testing


## API Base URL
`https://67aba1ae1fcfb0b6f0fdce74-lb-991.bm-southwest.lab.poridhi.io/notes`

## Database Information
- **Database**: MongoDB (notesdb)
- **Collection**: notes
- **Documents**: 3 total documents in collection

---

## API Endpoints Testing Results

### 1. POST /notes - Create New Note
![Create Note](./assets/createNote.png)
- **Method**: POST
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-991.bm-southwest.lab.poridhi.io/notes`
- **Content-Type**: application/json
- **Request Body**:
  ```json
  {
    "title": "Testing Note Creation",
    "content": "Creating first note through postman",
    "tags": []
  }
  ```
- **Expected Response**: 201 Created
- **Actual Response**: 201 Created
- **Response Body**:
  ```json
  {
    "_id": "685958ff33ead6990ecdf8aa",
    "title": "Testing Note Creation",
    "content": "Creating first note through postman",
    "tags": []
  }
  ```
- **Response Time**: 129ms
- **Response Size**: 947 B
- **Result**: ✅ Successfully creates note with auto-generated MongoDB ObjectId

### 2. GET /notes/{id} - Retrieve Single Note
![Get Single Note](./assets/getNoteById.png)
- **Method**: GET
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-991.bm-southwest.lab.poridhi.io/notes/68595469fb873f6e2d69e328`
- **Expected Response**: 200 OK
- **Actual Response**: 200 OK
- **Response Body**:
  ```json
  {
    "_id": "68595469fb873f6e2d69e328",
    "title": "Welcome Note",
    "content": "This is your first note! Welcome to the Notes API.",
    "tags": []
  }
  ```
- **Response Time**: 137ms
- **Response Size**: 988 B
- **Result**: ✅ Successfully retrieves specific note by ID

### 3. GET /notes - Retrieve All Notes
![Get All Notes](./assets/getNotes.png)
- **Method**: GET
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-991.bm-southwest.lab.poridhi.io/notes`
- **Expected Response**: 200 OK
- **Actual Response**: 200 OK
- **Response Body**: Array of note objects including:
  ```json
  [
    {
      "_id": "68595469fb873f6e2d69e328",
      "title": "Welcome Note",
      "content": "This is your first note! Welcome to the Notes API.",
      "tags": []
    },
    {
      "_id": "68595469fb873f6e2d69e329",
      "title": "Getting Started",
      "content": "You can create, read, update, and delete notes using the API endpoints.",
      "tags": []
    },
    {
      "_id": "685958ff33ead6990ecdf8aa",
      "title": "Testing Note Creation",
      "content": "Creating first note through postman",
      "tags": []
    }
  ]
  ```
- **Response Time**: 119ms
- **Response Size**: 1.1 KB
- **Result**: ✅ Successfully returns all notes in collection

### 4. PUT /notes/{id} - Update Note
![Update Note](./assets/putNote.png)
- **Method**: PUT
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-991.bm-southwest.lab.poridhi.io/notes/68595469fb873f6e2d69e328`
- **Content-Type**: application/json
- **Request Body**:
  ```json
  {
    "title": "Updating the note",
    "content": "Checking through postman",
    "tags": ["fastapi", "postman"]
  }
  ```
- **Expected Response**: 200 OK
- **Actual Response**: 200 OK
- **Response Body**:
  ```json
  {
    "_id": "68595469fb873f6e2d69e328",
    "title": "Updating the note",
    "content": "Checking through postman",
    "tags": [
      "fastapi",
      "postman"
    ]
  }
  ```
- **Response Time**: 484ms
- **Response Size**: 993 B
- **Result**: ✅ Successfully updates note with new title, content, and tags

### 5. DELETE /notes/{id} - Delete Note
![Delete Note](./assets/noteDeletion.png)
- **Method**: DELETE
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-991.bm-southwest.lab.poridhi.io/notes/68595469fb873f6e2d69e328`
- **Expected Response**: 200 OK
- **Actual Response**: 200 OK
- **Response Body**:
  ```json
  {
    "message": "Note deleted successfully"
  }
  ```
- **Response Time**: 116ms
- **Response Size**: 924 B
- **Result**: ✅ Successfully deletes note and returns confirmation message

### 6. GET /notes/search/{query} - Search Notes by Title
![Search Notes](./assets/searchByQuery.png)
- **Method**: GET
- **URL**: `https://67aba1ae1fcfb0b6f0fdce74-lb-991.bm-southwest.lab.poridhi.io/notes/search/Updating`
- **Expected Response**: 200 OK
- **Actual Response**: 200 OK
- **Response Body**:
  ```json
  [
    {
      "_id": "68595469fb873f6e2d69e328",
      "title": "Updating the note",
      "content": "Checking through postman",
      "tags": [
        "fastapi",
        "postman"
      ]
    }
  ]
  ```
- **Response Time**: 107ms
- **Response Size**: 993 B
- **Result**: ✅ Successfully searches and returns notes matching the query

---

## Database Verification
![MongoDB Collection](./assets/MongoExpressNotesCollection.png)

The MongoDB database shows:
- **Database Name**: notesdb
- **Collection**: notes
- **Total Documents**: 3 documents
- **Document Structure**: Each note contains `_id`, `title`, `content`, `created_at`, `updated_at`, and `tags` fields
- **Timestamps**: Proper UTC timestamps (Mon Jun 23 2025 13:19:37 GMT+0000)

---

## Testing Results Summary

All API endpoints are functioning correctly as evidenced by:

- ✅ **Proper HTTP Status Codes**: 200 OK, 201 Created
- ✅ **Correct JSON Response Formats**: Well-structured JSON responses
- ✅ **MongoDB Integration**: Successful database operations with proper ObjectId generation
- ✅ **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- ✅ **Search Functionality**: Text search working properly
- ✅ **Tag Support**: Arrays of tags properly handled
- ✅ **Response Times**: Excellent performance (107-484ms)
- ✅ **Error Handling**: Appropriate responses for various operations
- ✅ **Data Persistence**: Changes reflected in MongoDB collection

## Performance Metrics

| Operation | Response Time | Status | Size |
|-----------|---------------|--------|------|
| Create Note | 129ms | 201 Created | 947 B |
| Get Single Note | 137ms | 200 OK | 988 B |
| Get All Notes | 119ms | 200 OK | 1.1 KB |
| Update Note | 484ms | 200 OK | 993 B |
| Delete Note | 116ms | 200 OK | 924 B |
| Search Notes | 107ms | 200 OK | 993 B |

The Notes API deployment on the lab environment is stable, performant, and ready for production use with full MongoDB integration.
## 🔧 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   ```bash
   # Check if MongoDB container is running
   docker ps
   
   # Restart MongoDB
   docker-compose down
   docker-compose up -d
   ```

2. **Port Already in Use**
   ```bash
   # Check what's using port 27017 or 8000
   sudo lsof -i :27017
   sudo lsof -i :8000
   
   # Change ports in docker-compose.yml if needed
   ```

3. **Virtual Environment Issues**
   ```bash
   # Deactivate and recreate virtual environment
   deactivate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **ObjectId Validation Errors**
   ```bash
   # Ensure you're using valid MongoDB ObjectIds
   # Example valid ObjectId: 507f1f77bcf86cd799439011
   ```

---

## 🎯 Lab Completion Checklist

✅ **Environment Setup**
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt

✅ **MongoDB Setup**
- [ ] Docker Compose file configured
- [ ] MongoDB container running on port 27017
- [ ] Mongo Express accessible on port 8081
- [ ] Sample data initialized successfully

✅ **FastAPI Application**
- [ ] Application starts without errors
- [ ] Health check endpoint works
- [ ] Interactive documentation accessible

✅ **Notes CRUD Operations**
- [ ] Create note (POST /notes)
- [ ] Read all notes (GET /notes)
- [ ] Read specific note (GET /notes/{id})
- [ ] Update note (PUT /notes/{id})
- [ ] Delete note (DELETE /notes/{id})

✅ **Search Functionality**
- [ ] Search by title works
- [ ] Search by content works
- [ ] Search by tags works
- [ ] Case-insensitive search implemented

✅ **Error Handling**
- [ ] Invalid ObjectId returns 400
- [ ] Non-existent note returns 404
- [ ] Validation errors return appropriate messages

✅ **Testing**
- [ ] All endpoints tested with valid data
- [ ] Edge cases and error conditions tested
- [ ] Search functionality verified

---

## 🎓 Key Learning Outcomes

By completing this lab, you will understand:

1. **NoSQL Concepts**: Document-based storage vs relational databases
2. **Async Programming**: Non-blocking operations with async/await
3. **API Development**: RESTful principles and FastAPI implementation
4. **Data Validation**: Pydantic models for request/response validation
5. **MongoDB Operations**: CRUD operations and text search
6. **Docker**: Containerization for development environments
7. **Error Handling**: Proper HTTP status codes and error responses

This lab provides a solid foundation for building modern, scalable APIs with NoSQL databases and async Python frameworks.

---

## 🚧 Advanced Features (Optional Extensions)

### 1. Add Timestamps
```python
# Add to NoteModel
created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: Optional[datetime] = None
```

### 2. Implement Pagination
```python
@app.get("/notes")
async def get_notes(skip: int = 0, limit: int = 10):
    # Add pagination logic
```

### 3. Add Authentication
```python
# Implement JWT token authentication
from fastapi.security import HTTPBearer
```

### 4. Add Data Validation
```python
# Add more sophisticated validation rules
from pydantic import validator
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Python Asyncio Guide](https://docs.python.org/3/library/asyncio.html)

---