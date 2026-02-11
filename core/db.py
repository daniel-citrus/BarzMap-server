"""
Standalone database connection and Base for SQLAlchemy.
Used by ORM models to avoid circular imports (models must not import from services.Database).
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()


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
    return f"postgresql+psycopg://{user}@{host}:{port}/{database}"


APP_DATABASE_URL = os.getenv("APP_DATABASE_URL") or os.getenv("DATABASE_URL")
if not APP_DATABASE_URL:
    APP_DATABASE_URL = _build_database_url()
elif APP_DATABASE_URL.startswith("postgresql://"):
    APP_DATABASE_URL = APP_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

DATABASE_URL = APP_DATABASE_URL

engine = create_engine(
    APP_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
