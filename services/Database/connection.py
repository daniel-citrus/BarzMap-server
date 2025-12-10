"""
SQLAlchemy database connection and session management for BarzMap.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Helper function to construct database URL from components
def _build_database_url(
    user: str = None,
    password: str = None,
    host: str = None,
    port: str = None,
    database: str = None,
) -> str:
    """Build PostgreSQL connection URL from individual components."""
    user = user or os.getenv("POSTGRES_USER", "barzmap")
    password = password or os.getenv("POSTGRES_PASSWORD", "")
    host = host or os.getenv("POSTGRES_HOST", "localhost")
    port = port or os.getenv("POSTGRES_PORT", "5432")
    database = database or os.getenv("POSTGRES_DB", "barzmap")
    
    if password:
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"
    else:
        return f"postgresql+psycopg://{user}@{host}:{port}/{database}"

# Database URLs - supports both app user and superuser
# Priority: 1. APP_DATABASE_URL env var, 2. DATABASE_URL env var, 3. Build from components
APP_DATABASE_URL = os.getenv("APP_DATABASE_URL") or os.getenv("DATABASE_URL")
if not APP_DATABASE_URL:
    APP_DATABASE_URL = _build_database_url()
elif APP_DATABASE_URL.startswith("postgresql://"):
    APP_DATABASE_URL = APP_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Superuser URL (for administrative operations only)
# Falls back to APP_DATABASE_URL if not set
SUPERUSER_DATABASE_URL = os.getenv("SUPERUSER_DATABASE_URL") or APP_DATABASE_URL
if SUPERUSER_DATABASE_URL and SUPERUSER_DATABASE_URL.startswith("postgresql://"):
    SUPERUSER_DATABASE_URL = SUPERUSER_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)


# Legacy support: DATABASE_URL still works
DATABASE_URL = APP_DATABASE_URL

# Create SQLAlchemy engine for app user (default)
engine = create_engine(
    APP_DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query logging
    future=True  # Use SQLAlchemy 2.0 style
)

# Create SQLAlchemy engine for superuser (admin operations only)
superuser_engine = create_engine(
    SUPERUSER_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    future=True
)

# Create session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

SuperuserSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=superuser_engine,
    future=True
)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI to get database session using app user.
    
    This is the default and recommended connection for normal operations.
    
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


def get_superuser_db():
    """
    Dependency function for FastAPI to get database session using superuser.
    
    WARNING: Only use for administrative operations that require superuser privileges.
    Examples: creating databases, managing users, migrations.
    
    Usage in admin routes:
        from Database import get_superuser_db
        from sqlalchemy.orm import Session
        
        @app.post("/admin/create-database")
        def create_database(db: Session = Depends(get_superuser_db)):
            ...
    """
    db = SuperuserSessionLocal()
    try:
        yield db
    finally:
        db.close()

