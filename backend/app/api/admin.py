"""Admin API endpoints for configuration and scraping."""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import get_db
from app.models.scrape_job import ScrapeJob, JobStatus
from app.models.scraped_page import ScrapedPage
from app.scraper.scraper import run_scraper
from app.rag.rag_engine import get_rag_engine
from app.config import settings
from app.utils.logger import logger


router = APIRouter()


class ScrapeRequest(BaseModel):
    """Request to start a scrape job."""
    target_url: HttpUrl
    reindex: bool = True


class ConfigUpdate(BaseModel):
    """Configuration update request."""
    target_url: Optional[HttpUrl] = None
    scrape_frequency_hours: Optional[int] = None


class ScrapeJobResponse(BaseModel):
    """Scrape job response."""
    id: int
    target_url: str
    status: str
    pages_scraped: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class StatsResponse(BaseModel):
    """System statistics response."""
    total_pages: int
    total_chunks: int
    last_scrape: Optional[datetime]
    target_url: str
    scrape_frequency_hours: int


async def _run_scrape_job(job_id: int, target_url: str, reindex: bool, db_connection_string: str):
    """Background task to run scraping job."""
    from app.models.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Update job status
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        db.commit()
        
        # Run scraper
        pages_scraped = await run_scraper(db, target_url)
        
        # Update job with results
        job.pages_scraped = pages_scraped
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now()
        db.commit()
        
        # Reindex if requested
        if reindex:
            logger.info("Starting reindexing...")
            rag_engine = get_rag_engine()
            rag_engine.index_all_pages(db)
            logger.info("Reindexing completed")
        
    except Exception as e:
        logger.error(f"Scrape job {job_id} failed: {e}")
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.now()
        db.commit()
    finally:
        db.close()


@router.post("/scrape", response_model=ScrapeJobResponse)
async def start_scrape(
    scrape_request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start a new scraping job.
    
    Args:
        scrape_request: Scrape request with target URL
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Created scrape job
    """
    try:
        # Create new job
        job = ScrapeJob(
            target_url=str(scrape_request.target_url),
            status=JobStatus.PENDING
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start scraping in background
        background_tasks.add_task(
            _run_scrape_job,
            job.id,
            str(scrape_request.target_url),
            scrape_request.reindex,
            settings.database_url
        )
        
        logger.info(f"Started scrape job {job.id} for {scrape_request.target_url}")
        
        return ScrapeJobResponse(
            id=job.id,
            target_url=job.target_url,
            status=job.status.value,
            pages_scraped=job.pages_scraped,
            error_message=job.error_message,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to start scrape job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=List[ScrapeJobResponse])
async def get_jobs(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent scrape jobs.
    
    Args:
        limit: Maximum number of jobs to return
        db: Database session
        
    Returns:
        List of recent scrape jobs
    """
    jobs = db.query(ScrapeJob).order_by(desc(ScrapeJob.created_at)).limit(limit).all()
    
    return [
        ScrapeJobResponse(
            id=job.id,
            target_url=job.target_url,
            status=job.status.value,
            pages_scraped=job.pages_scraped,
            error_message=job.error_message,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at
        )
        for job in jobs
    ]


@router.get("/jobs/{job_id}", response_model=ScrapeJobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific scrape job by ID.
    
    Args:
        job_id: Job ID
        db: Database session
        
    Returns:
        Scrape job details
    """
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ScrapeJobResponse(
        id=job.id,
        target_url=job.target_url,
        status=job.status.value,
        pages_scraped=job.pages_scraped,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get system statistics.
    
    Args:
        db: Database session
        
    Returns:
        System statistics
    """
    total_pages = db.query(ScrapedPage).count()
    
    rag_engine = get_rag_engine()
    rag_stats = rag_engine.get_collection_stats()
    
    last_job = db.query(ScrapeJob).filter(
        ScrapeJob.status == JobStatus.COMPLETED
    ).order_by(desc(ScrapeJob.completed_at)).first()
    
    return StatsResponse(
        total_pages=total_pages,
        total_chunks=rag_stats.get('total_chunks', 0),
        last_scrape=last_job.completed_at if last_job else None,
        target_url=settings.target_url,
        scrape_frequency_hours=settings.scrape_frequency_hours
    )


@router.get("/homepage")
async def get_homepage(db: Session = Depends(get_db)):
    """
    Get the homepage HTML for pixel-perfect display.
    
    Args:
        db: Database session
        
    Returns:
        Homepage HTML and metadata
    """
    homepage = db.query(ScrapedPage).filter(
        ScrapedPage.is_homepage == True
    ).first()
    
    if not homepage:
        raise HTTPException(status_code=404, detail="Homepage not found. Please run scraping first.")
    
    return {
        'url': homepage.url,
        'title': homepage.title,
        'html': homepage.html,
        'scraped_at': homepage.scraped_at
    }
