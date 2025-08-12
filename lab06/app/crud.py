from sqlalchemy.orm import Session
from . import models, schemas

def get_note(db: Session, note_id: int):
    """Get a single note by ID"""
    return db.query(models.Note).filter(models.Note.id == note_id).first()

def get_notes(db: Session, skip: int = 0, limit: int = 100):
    """Get notes with pagination"""
    return db.query(models.Note).offset(skip).limit(limit).all()

def create_note(db: Session, note: schemas.NoteCreate):
    """Create a new note"""
    db_note = models.Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int):
    """Delete a note by ID"""
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()
        return True
    return False

def update_note(db: Session, note_id: int, note: schemas.NoteCreate):
    """Update a note"""
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note:
        db_note.title = note.title
        db_note.content = note.content
        db.commit()
        db.refresh(db_note)
        return db_note
    return None