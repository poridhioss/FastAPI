from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import asyncio

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from .cache import cache

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Redis Cache Lab", description="Notes API with Redis caching")

@app.get("/")
async def root():
    return {"message": "Redis Cache Lab - Notes API"}

# User endpoints
@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = crud.create_user(db=db, user=user)
    
    # Invalidate users cache
    await cache.delete_pattern("users:*")
    
    return new_user

@app.get("/users/{user_id}", response_model=schemas.UserWithNotes)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    cache_key = f"user:{user_id}:profile"
    
    # Try to get from cache first
    cached_user = await cache.get(cache_key)
    if cached_user:
        print(f"Cache HIT for user {user_id}")
        return cached_user
    
    print(f"Cache MISS for user {user_id}")
    
    # Get from database
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's notes
    user_notes = crud.get_user_notes(db, user_id=user_id)
    
    user_data = {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "notes": [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "user_id": note.user_id,
                "created_at": note.created_at,
                "updated_at": note.updated_at
            } for note in user_notes
        ]
    }
    
    # Cache the result for 5 minutes
    await cache.set(cache_key, user_data, expire=300)
    
    return user_data

@app.put("/users/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Invalidate user cache
    await cache.delete(f"user:{user_id}:profile")
    await cache.delete_pattern("users:*")
    
    return db_user

# Note endpoints
@app.get("/notes/{note_id}", response_model=schemas.Note)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    cache_key = f"note:{note_id}"
    
    # Try to get from cache first
    cached_note = await cache.get(cache_key)
    if cached_note:
        print(f"Cache HIT for note {note_id}")
        return cached_note
    
    print(f"Cache MISS for note {note_id}")
    
    # Get from database
    db_note = crud.get_note(db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note_data = {
        "id": db_note.id,
        "title": db_note.title,
        "content": db_note.content,
        "user_id": db_note.user_id,
        "created_at": db_note.created_at,
        "updated_at": db_note.updated_at
    }
    
    # Cache the result for 5 minutes
    await cache.set(cache_key, note_data, expire=300)
    
    return note_data

@app.post("/notes/", response_model=schemas.Note)
async def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = crud.get_user(db, user_id=note.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_note = crud.create_note(db=db, note=note)
    
    # Invalidate related caches
    await cache.delete(f"user:{note.user_id}:profile")
    await cache.delete_pattern("notes:*")
    
    return new_note

@app.put("/notes/{note_id}", response_model=schemas.Note)
async def update_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(get_db)):
    # Get the note to find user_id before updating
    db_note = crud.get_note(db, note_id=note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    updated_note = crud.update_note(db=db, note_id=note_id, note=note)
    
    # Invalidate caches
    await cache.delete(f"note:{note_id}")
    await cache.delete(f"user:{db_note.user_id}:profile")
    await cache.delete_pattern("notes:*")
    
    return updated_note

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    # Get the note to find user_id before deleting
    db_note = crud.get_note(db, note_id=note_id)
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    success = crud.delete_note(db=db, note_id=note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Invalidate caches
    await cache.delete(f"note:{note_id}")
    await cache.delete(f"user:{db_note.user_id}:profile")
    await cache.delete_pattern("notes:*")
    
    return {"message": "Note deleted successfully"}

@app.get("/notes/", response_model=List[schemas.Note])
async def get_all_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = crud.get_notes(db, skip=skip, limit=limit)
    return notes

# Cache management endpoints
@app.post("/cache/clear")
async def clear_cache():
    """Clear all cache entries"""
    await cache.delete_pattern("*")
    return {"message": "Cache cleared successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected", "cache": "connected"}