from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from typing import Generator
import os

# PostgreSQL setup with environment variable support
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/userdb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB setup with environment variable support
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGODB_URL)
mongo_db = mongo_client["activity_db"]
logs_collection = mongo_db["user_logs"]

def get_db() -> Generator:
    """Get PostgreSQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mongo():
    """Get MongoDB collection"""
    return logs_collection