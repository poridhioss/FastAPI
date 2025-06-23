from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List, Optional
import asyncio
from contextlib import asynccontextmanager

# Pydantic models
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class NoteModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = []
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = []

class NoteResponse(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    content: str
    tags: Optional[List[str]] = []
    
    class Config:
        allow_population_by_field_name = True

# Database connection
client: Optional[AsyncIOMotorClient] = None
database = None
notes_collection = None

async def connect_to_mongo():
    """Create database connection"""
    global client, database, notes_collection
    try:
        # MongoDB connection string for Docker container
        client = AsyncIOMotorClient("mongodb://admin:password123@localhost:27017/?authSource=admin")
        database = client.notesdb
        notes_collection = database.notes
        
        # Test the connection
        await client.admin.command('ismaster')
        print("✅ Connected to MongoDB successfully!")
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("🔌 Disconnected from MongoDB")

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

# Initialize FastAPI app
app = FastAPI(
    title="Notes API",
    description="A simple API to store and retrieve notes using MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Notes API is running!", "status": "healthy"}

@app.get("/notes", response_model=List[NoteResponse])
async def get_notes():
    """Retrieve all notes from MongoDB"""
    try:
        notes = []
        cursor = notes_collection.find({})
        async for document in cursor:
            # Convert ObjectId to string for JSON serialization
            document["_id"] = str(document["_id"])
            notes.append(NoteResponse(**document))
        
        return notes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notes: {str(e)}")

@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str):
    """Retrieve a specific note by ID"""
    try:
        if not ObjectId.is_valid(note_id):
            raise HTTPException(status_code=400, detail="Invalid note ID format")
        
        document = await notes_collection.find_one({"_id": ObjectId(note_id)})
        
        if document is None:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Convert ObjectId to string
        document["_id"] = str(document["_id"])
        return NoteResponse(**document)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving note: {str(e)}")

@app.post("/notes", response_model=NoteResponse, status_code=201)
async def create_note(note: NoteCreate):
    """Create a new note in MongoDB"""
    try:
        # Convert Pydantic model to dict
        note_dict = note.dict()
        
        # Insert into MongoDB
        result = await notes_collection.insert_one(note_dict)
        
        # Retrieve the inserted document
        created_note = await notes_collection.find_one({"_id": result.inserted_id})
        
        # Convert ObjectId to string
        created_note["_id"] = str(created_note["_id"])
        
        return NoteResponse(**created_note)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")

@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note: NoteCreate):
    """Update an existing note"""
    try:
        if not ObjectId.is_valid(note_id):
            raise HTTPException(status_code=400, detail="Invalid note ID format")
        
        # Update the note
        result = await notes_collection.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": note.dict()}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Retrieve the updated document
        updated_note = await notes_collection.find_one({"_id": ObjectId(note_id)})
        updated_note["_id"] = str(updated_note["_id"])
        
        return NoteResponse(**updated_note)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating note: {str(e)}")

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note by ID"""
    try:
        if not ObjectId.is_valid(note_id):
            raise HTTPException(status_code=400, detail="Invalid note ID format")
        
        result = await notes_collection.delete_one({"_id": ObjectId(note_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {"message": "Note deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")

@app.get("/notes/search/{query}")
async def search_notes(query: str):
    """Search notes by title or content"""
    try:
        # Create text search query
        search_filter = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query]}}
            ]
        }
        
        notes = []
        cursor = notes_collection.find(search_filter)
        async for document in cursor:
            document["_id"] = str(document["_id"])
            notes.append(NoteResponse(**document))
        
        return notes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching notes: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)