"""ScrapeJob model for tracking scraping jobs."""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from enum import Enum
from .database import Base


class JobStatus(str, Enum):
    """Scrape job status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapeJob(Base):
    """Model for scrape jobs."""

    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    pages_scraped = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    rag_indexed = Column(Integer, default=0)  # Number of chunks indexed in RAG
    last_successful_job_id = Column(Integer, nullable=True)  # Reference to last successful scraping job

    def __repr__(self):
        return f"<ScrapeJob(id={self.id}, status='{self.status}', pages={self.pages_scraped}, rag_indexed={self.rag_indexed})>"
