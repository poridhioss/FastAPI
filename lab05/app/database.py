from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from typing import Generator

# PostgreSQL setup
DATABASE_URL = "postgresql://postgres:password@localhost:5432/userdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
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