# Lab 6 – Search with Elasticsearch

## Goal:
Integrate Elasticsearch to index and search notes.

## Deliverables:
- On POST /notes, index note in Elasticsearch
- Add GET /search?q=keyword to search notes via Elasticsearch

## Elasticsearch
Elasticsearch is a distributed, RESTful search and analytics engine designed for horizontal scalability, reliability, and real-time search. It stores data as JSON documents and provides powerful capabilities for full-text search, filtering, and aggregation. It is widely used for log analytics, application monitoring, and search backends, and forms a key part of the Elastic Stack (ELK Stack) alongside Logstash and Kibana.

### How Elasticsearch Works: The Inverted Index
At the heart of Elasticsearch’s high-performance search is the inverted index, a data structure optimized for quick full-text lookups. Unlike traditional databases that scan rows for a query, Elasticsearch uses the inverted index to map terms to the documents that contain them.

#### Working Mechanism 
- Document Parsing: When a document is indexed, Elasticsearch breaks down text fields (like title or content) into tokens using analyzers (e.g., standard analyzer, which handles lowercasing, stopwords, stemming).
- Term Mapping: Each token is stored in the inverted index as a key, with a list of document IDs where that term appears. For example:
```arduino
"Elasticsearch" → [doc1, doc4, doc7]
"search"        → [doc2, doc3, doc4]
```
- Efficient Lookup: When a query arrives, Elasticsearch looks up the terms in the inverted index, quickly identifying the matching documents without scanning the full dataset.
- Scoring & Ranking: Elasticsearch calculates relevance scores (e.g., using TF-IDF or BM25) to rank documents, ensuring that the most relevant results appear first.
![Inverted Index](./assets/inverted%20index.png)

## PostgreSQL
PostgreSQL is a powerful, open-source object-relational database management system (ORDBMS) that emphasizes extensibility and SQL compliance. Known for its robustness, advanced features, and ACID compliance, PostgreSQL supports both relational and non-relational data types, making it suitable for a wide range of applications from web development to data analytics and geospatial applications.
How PostgreSQL Works: B-Tree Indexing
PostgreSQL uses various indexing mechanisms to optimize query performance, with B-Tree being the default and most commonly used index type. B-Tree indexes provide efficient data retrieval by organizing data in a balanced tree structure.
### Working Mechanism

#### Data Organization: 
PostgreSQL stores table data in pages (typically 8KB each) and uses B-Tree indexes to create a hierarchical structure that points to the actual data locations.
Balanced Tree Structure: The B-Tree maintains balance by ensuring all leaf nodes are at the same level, with internal nodes containing keys and pointers to child nodes:

Root Node: [25, 75]
    ├── [10, 20] → Points to data pages
    ├── [30, 50] → Points to data pages  
    └── [80, 90] → Points to data pages

#### Efficient Lookup: 
When a query searches for a specific value, PostgreSQL traverses the tree from root to leaf, using comparisons to navigate to the correct branch, significantly reducing the number of pages that need to be examined.
#### Query Optimization: 
PostgreSQL's query planner analyzes queries and chooses the most efficient execution path, deciding whether to use indexes, perform sequential scans, or combine multiple strategies.


## SQLAlchemy
SQLAlchemy is a popular Python SQL toolkit and Object-Relational Mapping (ORM) library that provides a high-level abstraction for interacting with relational databases. It offers both a Core system for direct SQL expression construction and an ORM system for mapping Python classes to database tables, making database operations more Pythonic and maintainable.

## pgAdmin
pgAdmin is a web-based administration and development platform for PostgreSQL databases. It provides a graphical user interface (GUI) that allows users to manage PostgreSQL databases, execute queries, and perform administrative tasks without using command-line tools.
### How pgAdmin Works: Web-Based Database Management
pgAdmin operates as a web application that connects to PostgreSQL servers and translates user interactions into SQL commands through an intuitive visual interface.
Working Mechanism

### Connection Management:
Stores connection details for multiple PostgreSQL servers, allowing easy switching between databases.
Object Browser: Displays database objects in a hierarchical tree structure for easy navigation and management.
Query Tool: Provides a SQL editor with syntax highlighting where users can write and execute queries interactively.
GUI to SQL Translation: Converts visual actions (like creating tables through forms) into appropriate SQL commands executed on the PostgreSQL server.

## Project Structure 
```
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── elasticsearch_client.py
│   └── crud.py
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```


## Project Workflow
![Process Workflow](./assets/architecture_diagram.png)

## Code Explanation
### models.py
This module defines the SQLAlchemy ORM models for the application. It maps Python classes to PostgreSQL tables, providing the schema for persistent storage.
#### Note Model
Represents a note in the database with the following fields:

- id (Integer, Primary Key) → Unique identifier for each note.

- title (String, max 255 chars) → Note title, indexed for faster queries.

- content (Text) → Main content of the note.

- created_at (DateTime) → Timestamp automatically set when the note is created.

-updated_at (DateTime) → Timestamp automatically updated whenever the note is modified.

#### Usage
- Provides the table schema for PostgreSQL.

- Used by SQLAlchemy ORM in CRUD operations and database migrations.

### schemas.py
This module defines Pydantic models used for request validation and response serialization in the API. It ensures type safety and consistent data formatting between FastAPI, the database, and Elasticsearch.

#### Note Base 
Base model with common fields for notes:

- title → Note title (1–255 characters).

- content → Note content (required).
#### NoteCreate 
It inerits from NodeBase

#### Note 
Extends notebase with more database generated files 
#### NoteSearchResult 
Includes Id, title, content, created_at and score(which represents relebance score from elasticsearch)

### database.py 
This module sets up the PostgreSQL database connection and session management using SQLAlchemy. It provides the foundation for all database interactions in the application.

#### Environment Loading
```python
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", ...)
```
Loads database credentials from .env, with a default fallback URL.

#### Engine 
```python
engine = create_engine(DATABASE_URL)
```
Creates the SQLAlchemy engine that manages connections to PostgreSQL

#### get_db() Dependency
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
Provides a session to FastAPI endpoints and ensures it is properly closed after the request.

### crud.py

#### get_note
```python
return db.query(models.Note).filter(models.Note.id == note_id).first()
```
Imports session for database accesss and imports the node model and pydantic schema 

#### get_notes 

```python
return db.query(models.Note).filter(models.Note.id == note_id).first()
```
Retrieves multiple notes from the database.
Supports pagination via skip (offset) and limit (maximum number of records).
Returns a list of Note objects.

#### create_note
```python
 db_note = models.Note(title=note.title, content=note.content)
db.add(db_note)
db.commit()
db.refresh(db_note)
return db_note
```
Creates a new Note object with the given title and content.
Adds it to the session and commits the transaction to save it in PostgreSQL.
db.refresh reloads the object to include auto-generated fields like id and created_at.
Returns the created note object.

#### delete_note
```python 
db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
if db_note:
    db.delete(db_note)
    db.commit()
    return True
return False
```
Looks up a note and deletes it and retruns true if note found otherwise returns false

#### update_note
```python 
db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
if db_note:
    db.delete(db_note)
    db.commit()
    return True
return False
```
Fetches a note and updates the note if note was found.

### elasticsearch_client.py

#### Initialization 
```python 
self.es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
self.index_name = os.getenv("ELASTICSEARCH_INDEX", "notes")
self.async_client = AsyncElasticsearch([self.es_url], ...)
self.sync_client = Elasticsearch([self.es_url], ...)
```
Sets Elasticsearch URL and index.
Creates async and sync clients with retries and timeout.

#### Create Index 
```python 
mapping = { "mappings": { "properties": { ... } }, "settings": { ... } }
exists = await self.async_client.indices.exists(index=self.index_name)
if not exists:
    await self.async_client.indices.create(index=self.index_name, body=mapping)

```
Checks if index exists; creates it with fields title, content, created_at.

#### Index note
```python 
doc = {"title": note.title, "content": note.content, "created_at": note.created_at.isoformat()}
await self.async_client.index(index=self.index_name, id=note.id, body=doc)
# sync version uses self.sync_client.index(...)
```
Stores a note in Elasticsearch. Supports async and sync operations.

#### Search Notes
```python 
search_body = {"query": {"multi_match": {"query": query, "fields": ["title^2","content"], "fuzziness":"AUTO"}}, ...}
response = await self.async_client.search(index=self.index_name, body=search_body)
```
Full-text search on title and content, sorts by _score and created_at.
Converts hits into NoteSearchResult objects with relevance score.

#### Delete Note
```python 
await self.async_client.delete(index=self.index_name, id=note_id)
# sync version uses self.sync_client.delete(...)
```
Deletes a note by ID. Async and sync versions available.

#### Close Clients 
```python 
await self.async_client.close()
self.sync_client.close()
```
Properly Closes the sync and async connection(needs awaits as async) 

### main.py 
This file defines the FastAPI application with PostgreSQL and Elasticsearch integration, providing endpoints for notes management, search, and health checks.

#### App Initialization & Elasticsearch
```python 
models.Base.metadata.create_all(bind=engine)  # Create database tables
app = FastAPI(title="Notes Search API", version="1.0.0")
es_client = ElasticsearchClient()  # Initialize Elasticsearch client

@app.on_event("startup")
async def startup_event():
    await es_client.create_index()  # Ensure Elasticsearch index exists
```
Creates database tables on startup.

Initializes Elasticsearch index automatically.

#### Root and health enpoints 
```python 
@app.get("/")
def read_root():
    return {"message": "Notes Search API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "notes-api"}

@app.get("/health/db")
def health_check_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))  # Simple query to check DB
    return {"status": "healthy", "service": "postgresql"}

@app.get("/health/elasticsearch")
async def health_check_elasticsearch():
    health = await es_client.health_check()
    return {"status": "healthy", "service": "elasticsearch", "cluster_status": health}
```
Basics API, database and health checks 

#### CRUD Endpoints 
##### Creating a note 
```python 
@app.post("/notes", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = crud.create_note(db=db, note=note)  # Save in PostgreSQL
    es_client.index_note_sync(db_note)  # Index in Elasticsearch (fire & forget)
    return db_note
```
Create a note in the dayabase and indexes it in Elasticsearch, elasticsearch indexing errors do not block note creation 

##### Get Notes and Single Note
```python 
@app.get("/notes", response_model=List[schemas.Note])
def get_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_notes(db, skip=skip, limit=limit)

@app.get("/notes/{note_id}", response_model=schemas.Note)
def get_note(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.get_note(db, note_id=note_id)
    if not db_note: raise HTTPException(status_code=404, detail="Note not found")
    return db_note
```
Supports paginanruon and fetvhing individual notes. 

##### Searching Notes in Elasticsearch 
```python 
@app.get("/search", response_model=List[schemas.NoteSearchResult])
async def search_notes(q: str, limit: int = 10):
    results = await es_client.search_notes(query=q, limit=limit)
    return results
```
Performs full-text search across title and content in Elasticsearch.

Returns results with relevance score and highlights.



### Dockerfile
- Base Image & Working Directory
```dockerfile
FROM python:3.11-slim
WORKDIR /app
```
Uses Python 3.11 slim for a lightweight container.

Sets /app as the working directory.

- Environment Variables 
```dockerfile 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
```
sends output directly to log 

- Installing system dependencies 
```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        && rm -rf /var/lib/apt/lists/*
```
Installs gcc for compiling python packages with c extensuons and cleans cache

- python dependency
```dockerfile
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
```
Copies requirements.txt and installs dependencies in the container.

Uses --no-cache-dir to keep image lean.
- Copy Application Port and Expose Port
```dockerfile
COPY app/ ./app/
COPY .env .

# Expose port
EXPOSE 8000
```

- Start Command 
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### docker-compose.yml
- PostgreSQL Service
```yaml 
postgresql:
  image: postgres:15-alpine
  environment:
    POSTGRES_USER: user
    POSTGRES_PASSWORD: password
    POSTGRES_DB: notesdb_lab06
  ports:
    - "5432:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U user"]
```
Runs a PostgreSQL 15 database.

Persists data using a Docker volume postgres_data.

Healthcheck ensures DB is ready before dependent services start.

- pgAdmin Service
```yaml
pgadmin:
  image: dpage/pgadmin4
  environment:
    PGADMIN_DEFAULT_EMAIL: admin@admin.com
    PGADMIN_DEFAULT_PASSWORD: admin
  ports:
    - "9000:80"
  depends_on:
    - postgresql
```
Provides a web UI to manage PostgreSQL.

Accessible at http://localhost:9000.

- Elasticsearch Service 
```yaml 
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
  environment:
    discovery.type: single-node
    xpack.security.enabled: false
    ES_JAVA_OPTS: "-Xms512m -Xmx512m"
  ports:
    - "9200:9200"
  volumes:
    - elasticsearch_data:/usr/share/elasticsearch/data
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
```
Runs Elasticsearch 8 in single-node mode.

Persists data in elasticsearch_data.

Healthcheck ensures the cluster is ready before FastAPI starts.

- FastAPI 
```yaml 
app:
  build: .
  ports:
    - "8000:8000"
  environment:
    - DATABASE_URL=postgresql://user:password@postgresql:5432/notesdb_lab06
    - ELASTICSEARCH_URL=http://elasticsearch:9200
  depends_on:
    postgresql:
      condition: service_healthy
    elasticsearch:
      condition: service_healthy
  volumes:
    - ./app:/app/app
    - ./.env:/app/.env
```
Builds the FastAPI app from local Dockerfile.

Waits for PostgreSQL and Elasticsearch to be healthy.

Exposes API on http://localhost:8000.

Uses local code and environment variables for live updates.
- Volumes and Networks 
```yaml 
volumes:
  postgres_data:
  elasticsearch_data:

networks:
  lab06_network:
    driver: bridge
```
 postgres_data and elasticsearch_data persist database and Elasticsearch data.

All services are on a single bridge network lab06_network for internal communication.

## PgAdmin Setup and Configuration

### Initial Setup

#### 1. Server Registration
1. Open PgAdmin in your browser
2. Right-click "Servers" in the Object Explorer
3. Select "Register" > "Server..."

#### 2. Connection Configuration

##### General Tab
- **Name**: `notesdb_lab06` (or your preferred server name)
- **Server group**: Servers
- **Connect now?**: Enable (toggle on)

![General Tab Configuration](./assets/pgadminsetup.png)

##### Connection Tab
- **Host name/address**: `postgresql` (or your database host)
- **Port**: `5432` (default PostgreSQL port)
- **Maintenance database**: `postgres`
- **Username**: `user` (or your database username)
- **Password**: Enter your database password
- **Save password?**: Enable for convenience

![Connection Tab Configuration](./assets/pgadminsetup2.png)

#### 3. Save Configuration
Click "Save" to register the server connection.

### Verification

#### Check Database Connection
1. Expand the server in Object Explorer
2. Navigate to: `Databases` > `notesdb_lab06` > `Schemas` > `public` > `Tables`
3. Right-click on a table (e.g., `notes`) and select "View/Edit Data" > "All Rows"
![Viweing Data](./assets/pgadmin_connection.png)


## Quick Start Guide

### Repository & Environment Setup

```bash
# Clone the repository
git clone clone https://github.com/poridhioss/FastAPI.git
cd FastAPI
cd lab06
```

### Creating dotenv 
```bash
touch .env
```
Then in the .env write 
```ini
# Database Configuration
DATABASE_URL=postgresql://user:password@postgresql:5432/notesdb_lab06

# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=notes

# Application Configuration
LOG_LEVEL=INFO
```

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


## Testing Notes Search API with Postman
### Base URL
```
https://67aba1ae1fcfb0b6f0fdce74-lb-836.bm-southwest.lab.poridhi.io
```

### API Endpoints

#### 1. Get API Info
- **Method:** `GET`
- **Endpoint:** `/`
- **Description:** Returns API version and basic information

![API Root](./assets/rootcheck.png)

#### 2. Health Checks

##### Database Health
- **Method:** `GET`
- **Endpoint:** `/health/db`
- **Description:** Checks PostgreSQL database connection

![Database Health](./assets/healthcheckdb.png)

##### Elasticsearch Health
- **Method:** `GET`
- **Endpoint:** `/health/elasticsearch`
- **Description:** Checks Elasticsearch service status

![Elasticsearch Health](./assets/healthcheck_elasticsearch.png)

#### 3. Notes Management

##### Get All Notes
- **Method:** `GET`
- **Endpoint:** `/notes`
- **Query Parameters:**
  - `skip`: Number of records to skip (default: 0)
  - `limit`: Maximum records to return (default: 100)

![Get Notes](./assets/getNote.png)

##### Get Single Note
- **Method:** `GET`
- **Endpoint:** `/notes/{note_id}`
- **Path Parameter:** `note_id` (integer)

![Get Note](./assets/getNote(Id).png)

##### Create Note
- **Method:** `POST`
- **Endpoint:** `/notes`
- **Body:** JSON
```json
{
  "title": "note01",
  "content": "desc"
}
```

![Create Note](./assets/postNote.png)

##### Delete Note
- **Method:** `DELETE`
- **Endpoint:** `/notes/{note_id}`
- **Path Parameter:** `note_id` (integer)

![Delete Note](./assets/deleteNote.png)

#### 4. Search Notes
- **Method:** `GET`
- **Endpoint:** `/search`
- **Query Parameters:**
  - `q`: Search query (required)
  - `limit`: Number of results (default: 10, max: 100)

![Search Notes](./assets/search.png)
