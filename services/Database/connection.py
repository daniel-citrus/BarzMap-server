"""
SQLAlchemy database connection and session management for BarzMap.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Database URL - defaults to local PostgreSQL
# Format: postgresql://username:password@localhost:5432/database_name
# Convert from JDBC format: jdbc:postgresql://localhost:5432/postgres
# To SQLAlchemy format: postgresql://localhost:5432/barzmap
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost:5432/barzmap"
)

# Create SQLAlchemy engine for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query logging
    future=True  # Use SQLAlchemy 2.0 style
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI to get database session.
    
    Usage in routes:
        from Database import get_db
        from sqlalchemy.orm import Session
        
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

