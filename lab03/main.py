# main.py
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
import os
from datetime import datetime

# Pydantic models for Pydantic v2
class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)


class NoteResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}


# FastAPI app
app = FastAPI(title="Notes API with MongoDB", version="1.0.0")

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "notesdb"
COLLECTION_NAME = "notes"

client = None
database = None
collection = None


@app.on_event("startup")
async def startup_db_client():
    global client, database, collection
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client[DATABASE_NAME]
    collection = database[COLLECTION_NAME]
    
    # Test connection
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")


@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()


@app.get("/")
async def root():
    return {"message": "Notes API with MongoDB", "status": "running"}


@app.get("/notes", response_model=List[NoteResponse])
async def get_notes():
    """Get all notes from the collection"""
    try:
        notes = []
        cursor = collection.find({})
        async for document in cursor:
            # Convert ObjectId to string for response
            document["_id"] = str(document["_id"])
            notes.append(document)
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notes: {str(e)}")


@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    """Get a specific note by ID"""
    try:
        if not ObjectId.is_valid(note_id):
            raise HTTPException(status_code=400, detail="Invalid note ID format")
        
        document = await collection.find_one({"_id": ObjectId(note_id)})
        if document:
            document["_id"] = str(document["_id"])
            return document
        else:
            raise HTTPException(status_code=404, detail="Note not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving note: {str(e)}")


@app.post("/notes", response_model=NoteResponse, status_code=201)
async def create_note(note: NoteCreate):
    """Create a new note"""
    try:
        # Create note document with timestamps
        note_dict = note.dict()
        note_dict["created_at"] = datetime.utcnow()
        note_dict["updated_at"] = datetime.utcnow()
        
        # Insert into MongoDB
        result = await collection.insert_one(note_dict)
        
        # Retrieve the created document
        created_note = await collection.find_one({"_id": result.inserted_id})
        created_note["_id"] = str(created_note["_id"])
        
        return created_note
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")


@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note: NoteCreate):
    """Update an existing note"""
    try:
        if not ObjectId.is_valid(note_id):
            raise HTTPException(status_code=400, detail="Invalid note ID format")
        
        # Update document with new timestamp
        update_data = note.dict()
        update_data["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Return updated document
        updated_note = await collection.find_one({"_id": ObjectId(note_id)})
        updated_note["_id"] = str(updated_note["_id"])
        
        return updated_note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating note: {str(e)}")


@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note"""
    try:
        if not ObjectId.is_valid(note_id):
            raise HTTPException(status_code=400, detail="Invalid note ID format")
        
        result = await collection.delete_one({"_id": ObjectId(note_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {"message": "Note deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint to verify MongoDB connection"""
    try:
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)