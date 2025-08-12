from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from .elasticsearch_client import ElasticsearchClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Notes Search API",
    description="FastAPI application with PostgreSQL and Elasticsearch integration",
    version="1.0.0"
)

# Initialize Elasticsearch client
es_client = ElasticsearchClient()

@app.on_event("startup")
async def startup_event():
    """Initialize Elasticsearch index on startup"""
    try:
        await es_client.create_index()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await es_client.close()
    logger.info("Application shutdown complete")

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Notes Search API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "notes-api"}

@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {"status": "healthy", "service": "postgresql"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.get("/health/elasticsearch")
async def health_check_elasticsearch():
    """Elasticsearch health check"""
    try:
        health = await es_client.health_check()
        return {"status": "healthy", "service": "elasticsearch", "cluster_status": health}
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        raise HTTPException(status_code=503, detail="Elasticsearch unavailable")

@app.post("/notes", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    """Create a new note"""
    try:
        # Save to PostgreSQL
        db_note = crud.create_note(db=db, note=note)
        logger.info(f"Created note with ID: {db_note.id}")
        
        # Index in Elasticsearch (fire and forget - don't fail if ES is down)
        try:
            es_client.index_note_sync(db_note)
            logger.info(f"Indexed note {db_note.id} in Elasticsearch")
        except Exception as es_error:
            logger.warning(f"Failed to index note in Elasticsearch: {es_error}")
        
        return db_note
    except Exception as e:
        logger.error(f"Failed to create note: {e}")
        raise HTTPException(status_code=500, detail="Failed to create note")

@app.get("/notes", response_model=List[schemas.Note])
def get_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all notes with pagination"""
    notes = crud.get_notes(db, skip=skip, limit=limit)
    return notes

@app.get("/notes/{note_id}", response_model=schemas.Note)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """Get a specific note by ID"""
    db_note = crud.get_note(db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@app.get("/search", response_model=List[schemas.NoteSearchResult])
async def search_notes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return")
):
    """Search notes using Elasticsearch"""
    try:
        results = await es_client.search_notes(query=q, limit=limit)
        logger.info(f"Search for '{q}' returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search service unavailable")

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a note"""
    try:
        # Delete from PostgreSQL
        deleted = crud.delete_note(db=db, note_id=note_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Remove from Elasticsearch (fire and forget)
        try:
            es_client.delete_note_sync(note_id)
            logger.info(f"Deleted note {note_id} from Elasticsearch")
        except Exception as es_error:
            logger.warning(f"Failed to delete note from Elasticsearch: {es_error}")
        
        return {"message": "Note deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete note: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete note")