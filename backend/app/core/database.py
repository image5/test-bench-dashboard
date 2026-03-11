"""
Database Configuration
SQLite Database - Windows Friendly
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

# Get the directory of this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data directory exists
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except Exception as e:
    print(f"[ERROR] Failed to create data directory: {e}")
    sys.exit(1)

# SQLite database path
DB_PATH = os.path.join(DATA_DIR, "test_bench.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
BaseModel = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database"""
    try:
        # Import models to register them
        from app.models.bench import TestBench
        from app.models.laboratory import Laboratory
        from app.models.alarm import Alarm
        from app.models.maintenance import MaintenanceRecord
        
        BaseModel.metadata.create_all(bind=engine)
        print(f"[OK] Database initialized: {DB_PATH}")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        raise
