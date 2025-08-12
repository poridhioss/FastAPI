from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NoteSearchResult(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    score: float = Field(..., description="Elasticsearch relevance score")