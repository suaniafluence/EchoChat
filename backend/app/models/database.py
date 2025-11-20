"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

from app.config import settings

# Create data directory if it doesn't exist
os.makedirs("./data", exist_ok=True)
os.makedirs("./logs", exist_ok=True)

# Database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Run database migrations for schema updates."""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)

    # Check if scrape_jobs table exists
    if 'scrape_jobs' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('scrape_jobs')]

        # Migration: Add rag_indexed column if it doesn't exist
        if 'rag_indexed' not in columns:
            with engine.connect() as conn:
                conn.execute(text('ALTER TABLE scrape_jobs ADD COLUMN rag_indexed INTEGER DEFAULT 0'))
                conn.commit()
                print("Migration: Added rag_indexed column to scrape_jobs table")

        # Migration: Add last_successful_job_id column if it doesn't exist
        if 'last_successful_job_id' not in columns:
            with engine.connect() as conn:
                conn.execute(text('ALTER TABLE scrape_jobs ADD COLUMN last_successful_job_id INTEGER'))
                conn.commit()
                print("Migration: Added last_successful_job_id column to scrape_jobs table")


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    run_migrations()
