"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
import stat
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create data directory with proper permissions if it doesn't exist
def ensure_directory_permissions(dir_path: str) -> None:
    """
    Ensure directory exists with write permissions.

    Args:
        dir_path: Path to directory
    """
    os.makedirs(dir_path, mode=0o755, exist_ok=True)

    # Verify and fix permissions on the directory
    try:
        current_mode = os.stat(dir_path).st_mode
        if not (current_mode & stat.S_IWUSR):  # Check if user has write permission
            logger.warning(f"Directory {dir_path} lacks write permissions. Fixing...")
            os.chmod(dir_path, 0o755)
            logger.info(f"Fixed permissions for directory: {dir_path}")
    except Exception as e:
        logger.error(f"Failed to check/fix directory permissions for {dir_path}: {e}")

# Ensure directories exist with proper permissions
ensure_directory_permissions("./data")
ensure_directory_permissions("./logs")

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
    # Ensure database file has write permissions
    if "sqlite" in settings.database_url:
        # Extract database file path from URL (format: sqlite:///./data/echochat.db)
        db_path = settings.database_url.replace("sqlite:///", "")
        if os.path.exists(db_path):
            try:
                current_mode = os.stat(db_path).st_mode
                if not (current_mode & stat.S_IWUSR):  # Check if user has write permission
                    logger.warning(f"Database file {db_path} lacks write permissions. Fixing...")
                    os.chmod(db_path, 0o644)
                    logger.info(f"Fixed permissions for database file: {db_path}")
            except Exception as e:
                logger.error(f"Failed to check/fix database file permissions: {e}")

    Base.metadata.create_all(bind=engine)
    run_migrations()
